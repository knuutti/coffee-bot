from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import cv2
from time import sleep
from datetime import datetime, timedelta
import threading
import subprocess
from coffee_library import analyse
from analysis import day_graph
from statistics import median

def main():
	
	print("Bot running")

	# Read the token file for connecting the bot
	tg_token = ""
	with open("tg_bot_token.txt") as tg_token_file:
		tg_token = tg_token_file.readline()

	# Returns the current status of the coffee machine
	async def coffee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		print("Request from user")
		#await update.message.reply_photo(photo=open('coffee.jpg', 'rb'))
		with open('coffee_coefficient.txt') as coffee_file:
			coffee = coffee_file.readline()
		if coffee:
			await update.message.reply_text(coffee)    

	# Debugging stuff
	async def debug_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		if update.message.from_user.username == "eknutars":
			await update.message.reply_text(subprocess.getoutput("ifconfig"))
			await update.message.reply_photo(photo=open('coffee.jpg', 'rb'))

	# Return graph of the day
	async def day_graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		await update.message.reply_photo(photo=open('day_graph.png', 'rb'))
		
	x = threading.Thread(target=main_thread)
	x.start()

	app = ApplicationBuilder().token(tg_token).build()
	app.add_handler(CommandHandler("kahvia", coffee))
	app.add_handler(CommandHandler("debug", debug_info))
	app.add_handler(CommandHandler("graph", day_graph))
	app.run_polling(allowed_updates=Update.ALL_TYPES)


	

def main_thread():
	
	history = []
	coffee_max = 0

	frequency = 5 # time in seconds of one update cycle

	is_brewing = False
	brew_time = None
	brew_reset = False 
	cups = 10
	reset_data = False

	while True:

		time = datetime.now()
		reset_data = clear_data(time, reset_data) # clear raw data at midnight

		img = get_image() # read image from the capture device
		coffee_level = analyse(img) # analyse the image and return the coffee level

		if coffee_level != -1:

			# Update the history for moving average
			if not len(history):
				history = 10 * [coffee_level]
			else:
				history.pop(0)
				history.append(coffee_level)

			# Using moving average to reduce noise in the input signal
			raw_level = coffee_level
			# coffee_level = sum(history)/len(history)
			coffee_level = median(history)

			# Value gets below zero level threshold -> able to start brewing again
			if not brew_reset and coffee_level < .15:
				brew_reset = True
				cups = 0
				coffee_max = 0

			# Value gets above the brew threshold -> start brewing
			if brew_reset and coffee_level > .2:
				brew_reset = False
				is_brewing = True
				brew_time = time

			# State: brewing or has finished brewing
			if not brew_reset:

				# Updating the amount of cups in the pot
				cups = get_cups(coffee_level)

				# Updating local max
				if coffee_level > coffee_max:
					coffee_max = coffee_level

				# Check if finished brewing
				if history[-1] - history[0] < 0.05 and is_brewing:
					is_brewing = False
					write_data('brew_data.csv', 'a', brew_time, get_cups(coffee_max))

			day_graph()
			
			update_telegram_message(cups, brew_time, is_brewing)
			write_data('data.csv', 'a', time, coffee_level)
			write_data('raw_data.csv', 'a', time, raw_level) # should be removed at some point

		# Updates every N seconds
		process_time = (datetime.now() - time).total_seconds()
		if process_time < frequency:
			sleep(frequency - process_time)


def get_image():
	c = cv2.VideoCapture(0)
	c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
	c.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
	_,img = c.read()
	c.release()
	return img

def get_cups(coffee_level: float):
	cups = 10
	if coffee_level < 0.15: cups = 0
	elif coffee_level < 0.2: cups = 1
	elif coffee_level < 0.25: cups = 2
	elif coffee_level < 0.3: cups = 3
	elif coffee_level < 0.35: cups = 4
	elif coffee_level < 0.4: cups = 5
	elif coffee_level < 0.5: cups = 6
	elif coffee_level < 0.6: cups = 7
	elif coffee_level < 0.7: cups = 8
	elif coffee_level < 0.8: cups = 9
	return cups

def write_data(fname, mode, time, value):
	data_file = open(fname, mode)
	data_file.write(str(time) + "," + str(value) + "\n")
	data_file.close()
	return None

def update_telegram_message(cups, brew_time, is_brewing):
	msg = "Kiltiksellä ei ole kahvia"
	if cups > 1: msg = f"Kiltiksellä on {cups} kuppia kahvia"
	elif cups == 1: msg = "Kiltiksellä on 1 kuppi kahvia"
	if brew_time:
		td = datetime.now()-brew_time
		th = td.total_seconds()//3600
		tm = (td.total_seconds()//60)-(60*th)
	if brew_time and not is_brewing and cups > 0:
		if th > 0:
			msg+=f" (keitetty {int(th)} h, {int(tm)} min sitten)"
		else:
			msg+=f" (keitetty {int(tm)} min sitten)"
	if is_brewing:
		msg = "Kahvia on tulossa"
		if brew_time:
			msg+=f" (keittäminen aloitettu ~{int(tm)} min sitten)"
	f = open('coffee_coefficient.txt', 'w')
	f.write(msg)
	f.close()
	return None

def clear_data(time: datetime, reset_data):
	if time.hour == 0 and not reset_data:
		new_file_name = str(time-timedelta(days=1))[0:10]
		data_file = open('data.csv', 'r')
		archive_file = open(f'data/{new_file_name}.csv', 'w')
		old_data = data_file.read().splitlines()
		for point in old_data:
			archive_file.write(str(point)+"\n")
		archive_file.close()
		data_file.close()
		data_file = open('data.csv', 'w')
		data_file.close()
		return True
	elif time.hour == 1 and reset_data:
		return False
	return reset_data



if __name__ == "__main__":
	main()