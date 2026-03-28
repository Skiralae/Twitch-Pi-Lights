#!/usr/bin/python3

import socket
import sys
import os
import _thread as thread
import json

# get creds from a file for safety
with open("svrcreds.json") as f:
    config = json.load(f)

client_id = config["client_id"]
token = config["bot_token"]
channel = config["channel"]

HOST = config["ip"]	# the listening IP
PORT = config["port"]           # the listening port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')

# Bind socket to local host and port
try:
	s.bind((HOST, PORT))
except (socket.error, msg):
	print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
	sys.exit()
	
print ('Socket bind complete')

# Start listening on socket, the size of queue is 10
s.listen(10)
print ('Socket now listening')

# Function for handling connections. This will be used to create threads
def clientthread(conn):
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		
		# Receiving from client
		data = conn.recv(1024)
		if not data: 
			break
		if (data.decode("utf-8") == 'LED ON'):
			reply = 'ON'
		else:
			reply = 'Welcome to the Server, ' + data.decode("utf-8") + '!' + os.linesep

		#https://www.geeksforgeeks.org/python/saving-text-json-and-csv-to-a-file-in-python/
		#log the data and reply to a file
		file = open("serverlog.txt", "a")
		file.write('\n' + str(data) + ' ' + str(addr[0]) + ':' + str(addr[1]) + '\n')
		file.write(str(reply) + '\n')
		file.close()

		print ('Welcome to the Server, ' + data.decode("utf-8") + '!')
		# force flush for nohup
		sys.stdout.flush()
	
		conn.sendall(reply.encode())
	
	# came out of loop if there is no data from the client
	conn.close()

# now keep talking with the client
while True:
    # wait to accept a connection - blocking call
    # it will wait/hang until a connection request is coming
	conn, addr = s.accept()
	print ('Connected with ' + addr[0] + ':' + str(addr[1]))
	
	# start new thread takes 1st argument as a function name to be run,
    # second is the tuple of arguments to the function.
	thread.start_new_thread(clientthread, (conn,))

s.close()
