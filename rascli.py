#!/usr/bin/python3

# Socket client example in python

import socket	#for sockets
import sys	    #for exit
from gpiozero import LED
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
blue = LED(4)
yellow = LED(27)
white = LED(26)
red = LED(13)
flashy = [blue, yellow, white, red]

#makes them flash alternating and progressively faster
async def ledFlash(light, sec):
	print("ledFlash called " + str(sec))
	for i in range(sec,0,-1):
		flashy[light].on()
		await asyncio.sleep(i)
		flashy[light].off()
		await asyncio.sleep(i)

async def ledBlink(light, num):
	print("ledBlink called " + str(num))
	for i in range(num):
		flashy[light].on()
		await asyncio.sleep(.1)
		flashy[light].off()
		await asyncio.sleep(.1)

#pulse three times then wait a second (num) times
async def ledPulse(light, num):
	print("ledPulse called " + str(num))
	for i in range(num):
		flashy[light].on()
		await asyncio.sleep(.2)
		flashy[light].off()
		await asyncio.sleep(.2)
		flashy[light].on()
		await asyncio.sleep(.2)
		flashy[light].off()
		await asyncio.sleep(.2)
		flashy[light].on()
		await asyncio.sleep(.2)
		flashy[light].off()
		await asyncio.sleep(1)


def isFree():
	for i in flashy:
		if (not i.is_lit):
			return 'READY'
	return 'NOT READY'

def tryLight(func, time):
	for i in range(numLights):
		if not flashy[i].is_lit and (tasks[i] is None or tasks[i].done()):
			#the later loop is lying, THIS is where it becomes a function call
			funcName = func
			tempFunc = globals()[funcName]
			print("calling " + funcName + " on light " + str(i))
			tasks[i] = asyncio.create_task(tempFunc(i, int(time)))
			return
		
# #try light doesn't work unless list is initialized
# def init():
# 	for i in range(numLights):
# 		tasks[i] = asyncio.create_task(ledFlash(flashy[i], 1))
# 		return
	
# #init it now
# init()

print ('Socket Connected to IP' + host)


async def main():
	#the blocking is preventing async lights
	s.setblocking(False)
	loop = asyncio.get_event_loop()
	# Send some data to remote server
	while True:
		await asyncio.sleep(.01)
		#see logic.txt for what is going on here
		#First make sure there is something new to do
		message1 = isFree() #checks if light is free
		try:
			# encode the string before sending
			await loop.sock_sendall(s, message1.encode()) #send light status to server
			# receive queue status from server
			reply1 = await loop.sock_recv(s, 4096)    # the maximum size of the data is 4096
			# decode the data to plain text
			input_str = reply1.decode("utf-8")
		except socket.error:
			# Send failed
			print ('Send failed')
			sys.exit()
			break
		#if lights are busy or queue is empty go back to step one
		if (message1 == 'NOT READY'):
			continue
		if (input_str == 'EMPTY'):
			continue
		#if there is something useful to do then do it
		reply2 = await loop.sock_recv(s, 4096)
		input_str2 = reply2.decode("utf-8")
		#should be getting a well-formed string that looks like a function call...
		print(input_str2)
		func_name, argument = input_str2.split(" ", 1)
		#...so just make it a function to call
		try:
			tryLight(func_name, int(argument))
			#f means formatted string 
		except Exception as e:
	            #f means formatted string
	            print(f"Error Type: {type(e).__name__} Error Details: {repr(e)}")
		

asyncio.run(main())




