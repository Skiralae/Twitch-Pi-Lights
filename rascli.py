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


# an array to track the async methods
tasks = [None] * numLights

timeCount = 0
message1 = ' '
message2 = ' '

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
s.connect((host, int(port)))

#initialize LEDS
GPIO.cleanup()
blue = LED(4)
yellow = LED(5)
white = LED(26)
red = LED(13)
flashy = [blue, yellow, white, red]





#makes them flash alternating and progressively faster
async def ledflash(light, sec):
	for i in range(sec,1,-1):
		light.on
		await asyncio.sleep(i)
		light.off
		await asyncio.sleep(i)

def isFree():
	for i in tasks:
		if (tasks[i] == None or tasks[i].done()):
			return 'READY'
	return 'NOT READY'

def tryLight(func):
	for i in tasks:
		if (tasks[i] == None or tasks[i].done()):
			tasks[i] = asyncio.create_task(func(flashy[i], argument))
			return

print ('Socket Connected to IP' + host)


# Send some data to remote server


while True:
	#see logic.txt for what is going on here
	#First make sure there is something new to do
	message1 = isFree() #checks if light is free
	try:
		# encode the string before sending
		s.sendall(message1.encode()) #send light status to server
	except socket.error:
		# Send failed
		print ('Send failed')
		sys.exit()
		break

	# receive queue status from server
	reply1 = s.recv(4096)    # the maximum size of the data is 4096
	# decode the data to plain text
	input_str = reply1.decode("utf-8")

	#if lights are busy or queue is empty go back to step one
	if (message1 == 'NOT READY'):
		continue
	if (input_str == 'EMPTY'):
		continue

	#if there is something useful to do then do it
	reply2 = s.recv(4096)
	input_str2 = reply2.decode("utf-8")
	#should be getting a well-formed string that looks like a function call...
	func_name, argument = input_str2.split(" ", 1)
	#...so just make it a function to call
	try:
		tryLight(func_name(argument))
	except:
		print('tryLight failed')
		
		



