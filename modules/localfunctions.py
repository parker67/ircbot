import socket, re, subprocess, os, time, threading, sys, time
import customlogging

class irc_comms(object):
	def connect(self, server, channel, botnick, password, lines):
		#regexes = [".*"]
		#combined = "(" + ")|(".join(regexes) + ")"
		ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ircsock.connect((server, 6667)) # Here we connect to the server using the port 6697
		ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n") # user authentication
		ircsock.send("NICK "+ botnick +"\n") # assign the nick to the bot
		ircsock.send("nickserv identify " + password + "\r\n")
		return ircsock

	def ping(self, ircsock): # respond to server Pings.
	  ircsock.send("PONG :pingis\n")  

	def sendmsg(self, msg, channel, ircsock): # sends messages to the channel.
	  ircsock.send("PRIVMSG "+ channel +" :"+ msg +"\n") 

	def joinchan(self, chan, ircsock): # join channel(s).
	#  time.sleep(5)
	  ircsock.send("JOIN "+ chan +"\n")
	#  customlogging.log("Joining %s" %chan)
	  return True

	def quitirc(self, ircsock):
	  ircsock.send("QUIT :Going to sleep\r\n")
	  sys.exit()

	def whisper(self, msg, user, ircsock): # whisper a user 
	  ircsock.send("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n')

	# log chat messages
	def logger(self, name, msg):
	  # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
	  irclog = open("ircchat.log", 'r')
	  content = irclog.readlines()
	  irclog.close()
	  # loop through the content of the chat log and reduce to 100 lines, starting with oldest. --Definitely a better way to do this, needs improvement.
	  irclog = open("ircchat.log", "w")
	  while len(content) > 100:
	    content.remove(content[0])
	  if len(content) > 0:
	    for i in content:
	      irclog.write(i.strip('\n\r') + '\n')
	  # write newest messge to log.
	  irclog.write(name + ':' + msg.strip('\n\r'))
	  irclog.close()

	# checks messages from find/replace before sending to the channel.
	def checksend(self, name,orig,new,ircsock,pattern=''):
	  # if the original message and new message are the same then do nothing.
	  if orig == new:
	    irc.whisper("No text would be changed.", name, ircsock)
	    return 
	  # if the find used very broad wildcards then do nothing. May need to add more or think of new method for this.
	  if pattern in {'\\s','\\S','\\D','\\W', '\\w'}:
	    irc.whisper("Wildcard(s) not allowed because they are too broad. If you meant to seach plaintext use 's/[find]/[replace]' or delimit the wildcard (like s|\\\\s|!s", name, ircsock)
	    return 
	  # if new message would be over 200 characters then do not send.
	  if len(new) > 200:
	    irc.whisper("Resulting message is too long (200 char max)", name, ircsock)
	    return
	  # if new message is empty string do not send.
	  if len(new) == 0:
	    irc.whisper("Replace resulted in empty messge. Nothing to send", name, ircsock)
	    return
	  # if message isn't caught by one of the checks, send to channel and log the message.
	  message="Correction, <" + name + ">: " + new
	  irc.sendmsg(message.strip('\r\n'), ircsock)
	  irc.logger(name, new, ircsock)

	# send help message to users
	def help(self, name,ircsock,topic=''):
	  # set default help message to blank.
	  message = ''
	  # if no help topic is specified, send general help message about the bot.
	  if topic == '':
	    message = "Hi! I am an irc bot created by OrderChaos. Currentl function is find and replace. You can perform a plain text find/replace on recent chat by typing in \'s/[find]/[replace]\' (no quotes) or a regex based find/replace with \'s|[find]|[replace]\'. Note that some wildcards are disabled because they result in too many matches. Please report any bugs or suggestions here: https://github.com/Orderchaos/ircbot/issues" 
	  # if a help message is specified, let the user know it's not coded yet.
	  else:
	    message = "Feature not yet implemented, sorry. Please see the main help (message me with \'.help\')"
	  customlogging.log(topic)
	  # send help message in whisper to user.
	  self.whisper(message, name, ircsock)

def get_statusid(message):
	message = message.split("/")
	status = message[-1]
	return status 

def get_youtubeid(message):
	message = message.split("=")
	youtube = message[-1]
	return youtube