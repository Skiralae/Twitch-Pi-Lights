#!/usr/bin/python3

# Socket client example in python

import socket	#for sockets
import sys	    #for exit
from gpiozero import LED
import RPi.GPIO as GPIO
import time
import json

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
orange = LED(5)
white = LED(26)

#makes them flash alternating and progressively faster
def ledflash():
	for i in range(5,1,-1):
		blue.on()
		white.off()
		time.sleep(i)
		blue.off()
		orange.on()
		time.sleep(i)
		orange.off()
		white.on()
		time.sleep(i)



print ('Socket Connected to IP' + host)

# Send some data to remote server
message = 'LED ON'

try:
	# encode the string before sending
	s.sendall(message.encode())
except socket.error:
	# Send failed
	print ('Send failed')
	sys.exit()

print ('Message has been sent successfully')

# receive data from server
reply = s.recv(4096)    # the maximum size of the data is 4096

# decode the data to plain text
if (reply.decode("utf-8") == 'ON'):
	ledflash()
else:
	print (reply.decode("utf-8"))

# close the socket to free the resources used by the socket
# s.close()


