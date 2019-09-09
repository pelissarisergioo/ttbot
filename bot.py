import RPi.GPIO as GPIO
import time
import event
from slackclient import SlackClient

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import requests

from picamera import PiCamera

RST = None
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0 



class Bot(object):
	def __init__(self):
		self.slack_client = SlackClient("xoxb-TOKEN")
		self.bot_name = "BOTNAME"
		self.bot_id = self.get_bot_id()
		
		if self.bot_id is None:
			exit("Error, could not find " + self.bot_name)
		
		# Init display
		self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
		self.disp.begin()
		self.disp.clear()
		self.disp.display()

		self.image = Image.new('1', (disp.width, disp.height))

		self.draw = ImageDraw.Draw(self.image)

		self.draw.rectangle((0, 0, width, height), outline=0, fill=0)
		self.font = ImageFont.load_default()

		self.prev_input = 1 
		self.is_room_free = True
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(22, GPIO.IN, pull_up_down= GPIO.PUD_UP)
			
		self.event = event.Event(self)
		self.listen()	

	def get_bot_id(self):
		api_call = self.slack_client.api_call("users.list")
		if api_call.get('ok'):
			# retrieve all users so we can find our bot
			users = api_call.get('members')
			for user in users:
				if 'name' in user and user.get('name') == self.bot_name:
					return "<@" + user.get('id') + ">"
			
			return None
			
	def drawStatus(self):
		self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
		text = 'Room Free' if self.is_room_free else 'Room Occupied'
		self.draw.text((0, -2), text, font=self.font, fill=255)
		self.disp.image(self.image)
		self.disp.display()
		
	def listen(self):
		if self.slack_client.rtm_connect(with_team_state=False):
			print("Successfully connected, listening for commands")
			while True:
				self.event.wait_for_event()
				input = GPIO.input(22)
				if ((not self.prev_input) and input):
					print('BUTTON PRESSED')
					self.is_room_free = not self.is_room_free
					slack_text = ":table_tennis_paddle_and_ball: Table Tennis room is now free" if self.is_room_free else ":table_tennis_paddle_and_ball: Someone is now playing TT"
					#TODO: send message to slack
				self.prev_input = input
				self.drawStatus()
				time.sleep(1)
		else:
			exit("Error, Connection Failed")
