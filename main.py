#!/usr/bin/python

# Import some necessary libraries.
import socket, re, subprocess, os, time, threading, sys, time

#from customlogging import customlog
from modules.localfunctions import *
from modules.customlogging import *

customlogging.customlog()
# Some basic variables used to configure the bot        
server = "192.168.1.110" # Server
channel = "##bot-testing" # Channel
lines = 0
botnick = "Python-IRC" # Your bots nick
password = ""
ircsock = connect(server,channel,botnick,password,lines)

# main functions of the bot
def main():
  # start by joining the channel. --TO DO: allow joining list of channels
  if joinchan(channel, ircsock) != True:
    exit("Error joining channel")
  # open the chat log file if it exists and delete it to start fresh.
  with open("ircchat.log", "w") as temp:
    temp.write("Joined channel")
  # start infinite loop to continually check for and receive new info from server
  time.sleep(5)
  joinchan(channel, ircsock)
  while 1: 
    try:
       # clear ircmsg value every time
       ircmsg = ""
       # set ircmsg to new data received from server
       ircmsg = ircsock.recv(2048)
       # remove any line breaks
       ircmsg = ircmsg.strip('\n\r') 
       # customlogging.log received message to stdout (mostly for debugging).
       customlogging.log(ircmsg) 
       # repsond to pings so server doesn't think we've disconnected
       if ircmsg.find("PING :") != -1: 
         ping()
       # look for PRIVMSG lines as these are messages in the channel or sent to the bot
       if ircmsg.find("PRIVMSG") != -1:
         # save user name into name variable
         name = ircmsg.split('!',1)[0][1:]
         customlogging.log('name: ' + name)
         # get the message to look for commands
         message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
         customlogging.log(message)
         # look for commands and send to appropriate function.
         if message[:2] == 's|':
           regex(message, ircsock)
         elif message[:2] == 's/':
           sed(message, ircsock)
         elif message[:5] == '.help':
           help(name,ircsock,message[5:])
         else:
         # if no command found, get 
           if len(name) < 17:
             logger(name, message, ircsock)
             # if the final message is from me and says 'gtfo [bot]' stop the bot and exit. Needs adjustment so it works for main user account and not hardcoded username.
             if name.lower() == "orderchaos" and message[:5+len(botnick)] == "gtfo %s" % botnick:
               sendmsg("Oh...okay... :'(", ircsock)
               ircsock.send("PART " + channel + "\r\n")
               sys.exit()
    except KeyboardInterrupt:
      customlogging.log("Caught ctrl C")
      quitirc(ircsock)

#start main functioin
main()

