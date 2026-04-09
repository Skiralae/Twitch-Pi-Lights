#!/usr/bin/python3

# Socket client example in python

import socket	#for sockets
import sys	    #for exit
from gpiozero import LED
import RPi.GPIO as GPIO
import time
import json
import asyncio

numLights = 4 #must be 1 or greater
numUsable = numLights - 1 #I'm leaving one light as a status light

# an array to track the async methods
tasks = None * numUsable 

timeCount = 0
message = ' '

# create an INET(IPv4), STREAMing(TCP) socket
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	print ('Failed to create socket')
	sys.exit()
	
print ('Socket Created')


# get creds from a file for safety
with open("clicreds.json") as f:
    config = json.load(f)

host = config["ip"]   # the IP address of the server to connect
port = config["port"] # the port number of the application

# Connect to remote server
s.connect((host, port))

#initialize LEDS
GPIO.cleanup()
blue = LED(4)
yellow = LED(5)
white = LED(26)
#red is special and will not run the commands
flashy = [blue, yellow, white]

red = LED(13)



#makes them flash alternating and progressively faster
async def ledflash(light, sec):
	for i in range(sec,1,-1):
		light.on
		await asyncio.sleep(i)
		light.off
		await asyncio.sleep(i)

def tryLight(func):
	for i in tasks:
		if (tasks[i] == None or tasks[i].done()):
			tasks[i] = asyncio.create_task(func(flashy[i], 4))
			return
	message = 'FULL'

print ('Socket Connected to IP' + host)


# Send some data to remote server


while True:
	try:
		# encode the string before sending
		s.sendall(message.encode())
	except socket.error:
		# Send failed
		print ('Send failed')
		sys.exit()
		break

	print ('Message has been sent successfully')

	# receive data from server
	reply = s.recv(4096)    # the maximum size of the data is 4096

	# decode the data to plain text
	if (reply):
		input_str = reply.decode("utf-8")
		func_name, argument = input_str.split(" ", 1)
		try:
			tryLight(func_name(argument))
		finally:
			timeCount = 0
	else: 
		timeCount += 1
		if timeCount > 4000:
			s.close
			print("Connection timeout")
		



