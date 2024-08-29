from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import cv2
from time import sleep
from datetime import datetime, timedelta
import threading
from coffee_library import analyse

def main():
	
	print("Bot running")

	tg_token = ""
	with open("tg_bot_token.txt") as tg_token_file:
		tg_token = tg_token_file.readline()

	async def coffee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		print("Request from user")
		#await update.message.reply_photo(photo=open('coffee.jpg', 'rb'))
		with open('coffee_coefficient.txt') as coffee_file:
			coffee = coffee_file.readline()
		if coffee:
			await update.message.reply_text(coffee)    

	# Debugging
	async def debug_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		if update.message.from_user.username == "eknutars":
			# await update.message.reply_text(subprocess.getoutput("ifconfig"))
			await update.message.reply_photo(photo=open('coffee.jpg', 'rb'))
		
	x = threading.Thread(target=threading_function)
	x.start()

	app = ApplicationBuilder().token(tg_token).build()
	app.add_handler(CommandHandler("kahvia", coffee))
	app.add_handler(CommandHandler("debug", debug_info))
	app.run_polling(allowed_updates=Update.ALL_TYPES)


	

def threading_function():
	
	prevs = [0,0,0]
	is_brewing = False
	brew_time = None
	brew_reset = True
	cups = 10
	reset_data = False

	while True:

		start_time = datetime.now()
		reset_data = clear_data(start_time, reset_data) # clear raw data at midnight

		img = get_image() # read image from the capture device
		coffee_level = analyse(img) # analyse the image and return the coffee level

		# Post new data point
		if coffee_level > 0:

			if not brew_reset and coffee_level < .2:
				brew_reset = True

			# If counter reaches 0 at one point, random errors won't affect the output
			if cups > 0 or coffee_level > 0.15:
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
				else: cups = 10

			
			update_telegram_message(cups, brew_time, is_brewing)
			
			print("Coffee level:", coffee_level)

			data_file = open('data.csv', 'a')
			data_file.write(str(start_time)+","+str(coffee_level)+"\n")
			data_file.close()

			prevs[0],prevs[1],prevs[2] = prevs[1],prevs[2],coffee_level

			if prevs[1]-prevs[0]>.02 and prevs[2]-prevs[1]>.02 and brew_reset and coffee_level > .2:
				is_brewing = True
				brew_reset = False
				brew_time = start_time
			elif prevs[1]-prevs[0]<.02 and prevs[2]-prevs[1]<.02:
				if is_brewing:
					is_brewing = False
					# Update brew time as current time
					brew_time = datetime.now()
					data_file = open('brew_data.csv', 'a')
					data_file.write(str(brew_time)+","+str(cups)+"\n")
					data_file.close()

		
		sleep(15-(datetime.now()-start_time).total_seconds())


def get_image():
	c = cv2.VideoCapture(0)
	c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
	c.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
	_,img = c.read()
	c.release()
	return img

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