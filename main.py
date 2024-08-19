from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import cv2
import numpy as np
from time import sleep
from datetime import datetime
import threading
from math import ceil, floor
import subprocess

import coffee_library as cl

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
			await update.message.reply_text(subprocess.getoutput("ifconfig"))
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

	while True:

		# Taking a picture
		c = cv2.VideoCapture(0)
		c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
		c.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
		start_time = datetime.now()
		_,img = c.read()
		c.release()
		
		# Reading the current coffee level
		coffee_level = cl.analyse(img)

		# Post new data point
		if coffee_level != -1:
			time_stamp = datetime.now()

			if not brew_reset and coffee_level < .2:
				brew_reset = True

			# If counter reaches 0 at one point, random errors won't affect the output
			if cups > 0 or coffee_level > 0.2:
				cups = floor(coffee_level*10)
			
			msg = "Kiltiksellä ei ole kahvia"
			if cups > 1: msg = f"Kiltiksellä on {cups} kuppia kahvia"
			elif cups == 1: msg = "Kiltiksellä on 1 kuppi kahvia"
			if brew_time:
				td = datetime.now()-brew_time
				th = td.total_seconds()//3600
				tm = (td.total_seconds()//60)-(60*th)
			if brew_time and not is_brewing and cups > 0: 
				#ts = td.total_seconds()-(3600*th+60*tm)
				if th > 0:
					msg+=f" (keitetty {round(th)} h, {round(tm)} min sitten)"
				else:
					msg+=f" (keitetty {tm} min sitten)"
			if is_brewing:
				msg = "Kahvia on tulossa"
				if brew_time:
					msg+=f" (keittäminen aloitettu ~{round(tm)} min sitten)"
					
			f = open('coffee_coefficient.txt', 'w')
			f.write(msg)
			f.close()
			data_file = open('data.csv', 'a')
			data_file.write(str(time_stamp)+","+str(coffee_level)+"\n")
			data_file.close()

			prevs[0],prevs[1],prevs[2] = prevs[1],prevs[2],coffee_level

			if prevs[1]-prevs[0]>.02 and prevs[2]-prevs[1]>.02 and brew_reset and coffee_level > .2:
				is_brewing = True
				brew_reset = False
				brew_time = time_stamp
			elif prevs[1]-prevs[0]<.02 or prevs[2]-prevs[1]<.02:
				if is_brewing:
					is_brewing = False
					# Update brew time as current time
					brew_time = datetime.now()
					data_file = open('brew_data.csv', 'a')
					data_file.write(str(brew_time)+","+str(ceil(coffee_level*10))+"\n")
					data_file.close()

		
		sleep(15-(datetime.now()-start_time).total_seconds())


		


if __name__ == "__main__":
	main()