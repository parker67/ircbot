#!/usr/bin/python

# Import some necessary libraries.
import socket, re, subprocess, os, time, threading, sys, time
from modules.localfunctions import *
from modules.customlogging import *
from modules.twit import *

customlog = customlogging.customlog()
irc = irc_comms()
# Some basic variables used to configure the bot        
server = "" # Server
channel = "" # Channel
lines = 0
botnick = "" # Your bots nick
password = ""
ircsock = irc.connect(server,channel,botnick,password,lines)

# main functions of the bot
def main():
  # start by joining the channel. --TO DO: allow joining list of channels
  if irc.joinchan(channel, ircsock) != True:
    exit("Error joining channel")
  # open the chat log file if it exists and delete it to start fresh.
  with open("ircchat.log", "w") as temp:
    temp.write("Joined channel")
  # start infinite loop to continually check for and receive new info from server
  time.sleep(5)
  irc.joinchan(channel, ircsock)
  while 1: 
    try:
       # clear ircmsg value every time
       ircmsg = ""
       # set ircmsg to new data received from server
       ircmsg = ircsock.recv(2048)
       # remove any line breaks
       ircmsg = ircmsg.strip('\n\r') 
       # customlogging.cust_log received message to stdout (mostly for debugging).
       customlog.cust_log(ircmsg) 
       # repsond to pings so server doesn't think we've disconnected
       if ircmsg.find("PING :") != -1: 
         irc.ping(ircsock)
       # look for PRIVMSG lines as these are messages in the channel or sent to the bot
       if ircmsg.find("PRIVMSG") != -1:
         # save user name into name variable
         name = ircmsg.split('!',1)[0][1:]
         customlog.cust_log('name: ' + name)
         # get the message to look for commands
         message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
         customlog.cust_log('message: ' + message)
         # look for commands and send to appropriate function.
         if message[:5] == '.help':
           irc.help(name,ircsock,message[5:])
         elif message.find("twitter.com") != -1:
           if message.find("status") != -1:
            customlog.cust_log("Caught twitter")
            irc.sendmsg("Oh...okay... looking up tweet. Please wait", channel, ircsock)
            stat = get_statusid(message)
            twitter = twit_worm()
            name, status = twitter.get(stat)
            name = "Name: " + name
            status = "Status: " + status
            irc.sendmsg(name, channel, ircsock)
            irc.sendmsg(status, channel, ircsock)
           else:
            customlog.cust_log("Not a status page")
            irc.sendmsg("Sorry that doesnt look to be a valid twitter status page. Please try again", channel, ircsock)
         elif message.find("youtube.com") != -1:
           if message.find("watch") != -1:
            customlog.cust_log("Caught youtube")
            irc.sendmsg("Oh...okay... looking up youtube video. Please wait", channel, ircsock)
            youtubeid = get_youtubeid(message)
            youtub = youtube()
            title, chan = youtub.get_title(youtubeid)
            title = "Video: " + title
            chan = "Channel Title: " + chan
            irc.sendmsg(title, channel, ircsock)
            irc.sendmsg(chan, channel, ircsock)
         else:
         # if no command found, get 
           if len(name) < 17:
             irc.logger(name, message)
             # if the final message is from me and says 'gtfo [bot]' stop the bot and exit. Needs adjustment so it works for main user account and not hardcoded username.
             if name.lower() == "spiderdan" and message[:5+len(botnick)] == "gtfo %s" % botnick:
               irc.sendmsg("Oh...okay... :'(", channel, ircsock)
               irc.quitirc(ircsock)
    except KeyboardInterrupt:
      customlog.cust_log("Caught ctrl C")
      irc.quitirc(ircsock)

#start main functioin
main()

