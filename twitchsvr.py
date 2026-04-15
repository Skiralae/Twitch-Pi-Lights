#!/usr/bin/python3

import socket
import sys
import os
import _thread as thread
import json
import webbrowser

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.oauth import refresh_access_token
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio

# get creds from a file for safety
with open("svrcreds.json") as f:
    config = json.load(f)

client_id = config["client_id"]
client_secret = config["client_secret"]
access_token = config["bot_access_token"]
refresh_token = config["bot_refresh_token"]
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
channel = config["channel"]

HOST = config["ip"]	  # the listening IP
PORT = config["port"] # the listening port

commandQueue = asyncio.Queue(maxsize=5)
recieveQueue = asyncio.Queue()

# The following is modified from twitch's documentation:
# https://pytwitchapi.dev/en/stable/
# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(channel)
    # you can do other bot initialization things in here


# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\\n'
          f'  Type: {sub.sub_plan}\\n'
          f'  Message: {sub.sub_message}')


# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

# this will be called whenever the !reply command is issued
async def queue_command(cmd: ChatCommand):
    #if the command is valid and queue is not full, put command on queue
    if len(cmd.parameter) > 0 and not commandQueue.full():
        commandQueue.put(cmd.name + " " + cmd.parameter)
        
        


# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(client_id, client_secret)
    # auth = UserAuthenticator(twitch, USER_SCOPE)
    await twitch.set_user_authentication(access_token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    chat.register_command('reply', test_command)
    chat.register_command('ledFlash', queue_command)


    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()


# lets run our setup
asyncio.run(run())

#Socket connection time!
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
        # if the queue has items, pop next and sent it
        elif not commandQueue.empty():
            commandQueue.join()
            reply = commandQueue.get()
        else:
            reply = commandQueue.full()
        
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
