import socket, re, subprocess, os, time, threading, sys, time
import customlogging

def connect(server, channel, botnick, password, lines):
	#regexes = [".*"]
	#combined = "(" + ")|(".join(regexes) + ")"
	ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ircsock.connect((server, 6667)) # Here we connect to the server using the port 6697
	ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n") # user authentication
	ircsock.send("NICK "+ botnick +"\n") # assign the nick to the bot
	ircsock.send("nickserv identify " + password + "\r\n")
	return ircsock

def ping(ircsock): # respond to server Pings.
  ircsock.send("PONG :pingis\n")  

def sendmsg(msg, ircsock): # sends messages to the channel.
  ircsock.send("PRIVMSG "+ channel +" :"+ msg +"\n") 

def joinchan(chan, ircsock): # join channel(s).
#  time.sleep(5)
  ircsock.send("JOIN "+ chan +"\n")
#  customlogging.log("Joining %s" %chan)
  return True

def quitirc(ircsock):
  ircsock.send("QUIT :Going to sleep\r\n")
  sys.exit()

def whisper(msg, user, ircsock): # whisper a user 
  ircsock.send("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n')

# Plaintext Find/Replace.
def sed(msg, ircsock):
  # detect if there are fewer than 2 '/' in the message. If so, not a valid find/replace pair, do nothing.
  if msg.count('/') < 2:
    customlogging.log("not enough arguments")
    return
  # get the text between the first and last '/' as the 'find' portion
  sedtest=msg.split('/',1)[1].rsplit('/',1)[0]
  # if there is no text between the first and last '/' (as in 's//somethin') do nothing because there is nothing to find.
  if sedtest == '':
    customlogging.log("Nothing to find")
    return
  # set the replace text to everything after the last '/'
  sreplace=msg.split('/',1)[1].rsplit('/',1)[1]
  # set the default replaced text to a known, default value
  replaced = ".__not found__."
  # read in the chat log file
  with open("ircchat.log", "r") as ircchat:
    content = ircchat.readlines() 
  # loop through the chat log and search through the messages for a match to the 'find' string. Ignore any errors -- to be fixed.
  for i in content:
    try:
      if i.split(':',1)[1].find(sedtest) != -1:
        replaced = i
    except Exception:
      pass
  # if the default replaced text was not changed, no matches were found in the log, do nothing.
  if replaced == ".__not found__.":
    customlogging.log("not found")
    return
  else:
  # if the default replaced text was found, perform a replace on the text, strip any newlines, and send to checksend method for verification before sending to channel.
    name = replaced.split(':', 1)[0]
    replaced = replaced.split(':',1)[1].replace(sedtest, sreplace)
    replaced = replaced.strip('\n\r')
    checksend(name,sedtest, replaced, ircsock)

# Regex Find/Replace
def regex(msg, ircsock):
  #detect if there are fewer than 2 '|' in the message. If so, not a valid find/replace pair, do nothing.
  if msg.count('|') < 2:
    customlogging.log("Not enough arguments")
    return
  # get the text between the first and last '|' as the 'find portion
  sedtest = msg.split('|',1)[1].rsplit('|',1)[0]
  # if there is no text between the first and last '|' (as in 's||somethin') do nothing because there is nothing to find.
  if sedtest == '':
    customlogging.log("Nothing to find")
    return
  # set the replace text to everything after the last '|'
  sreplace = msg.split('|',1)[1].rsplit('|',1)[1]
  # set the default replaced text to a known, default value
  replaced = ".__not found__."
  # escape any '*' wildcards as they are too broad so assume they are literal. Needs testing for '\*' searches.
  if (sedtest.find("*") != -1):
    findme = sedtest.replace('*','\*')
  # if find is a single character, escape it because it any regex would be too broad.
  elif len(sedtest) == 1:
    findme = re.escape(sedtest)
  else:
  # if neither of the other two are true, set the find string.
    findme = sedtest
  try:
  # set the pattern to find 
    pattern = re.compile("(%s)" % findme)
  except Exception:
  # if there is an error, escape the find string and try again. --Needs further testing.
    findme = re.escape(findme)
    pattern = re.compile("(%s)" % findme)
    pass
  # Read in the chat log
  with open("ircchat.log", "r") as ircchat:
    content = ircchat.readlines()
  # set default replaced text, username, and found string
  repltext = ('',0)
  name = ''
  found = ''
  # loop through chat log
  for i in content:
    try:
      # set text equal to just the message, no username.
      text = i.split(":",1)[1]
      # search the text for regex pattern, if found, set found equal to the text and replace it with replace string. Set name equal to the username of found message.
      if pattern.search(text):
        text = text.strip('\n\r')
        found = text
        repltext = re.subn(pattern, sreplace, text)
        name = i.split(":",1)[0]
    # ignore errors and continue. --Needs further testing
    except Exception:
      customlogging.log('error in search')
      pass
  # if the regex found more than 10 matches, assume it was too broad and let the user know. --Change to whisper?
  if repltext[1] > 10:
    sendmsg("Too many matches, refine your correction", ircsock)
    return
  # set replaced string equal to just the new message and strip newlines, then send to checksend for verification before sending to channel.
  replaced = repltext[0]
  replaced = replaced.strip('\n\r')
  checksend(name,found, replaced, findme, ircsock)

# log chat messages
def logger(name, msg):
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
def checksend(name,orig,new,ircsock,pattern=''):
  # if the original message and new message are the same then do nothing.
  if orig == new:
    whisper("No text would be changed.", name, ircsock)
    return 
  # if the find used very broad wildcards then do nothing. May need to add more or think of new method for this.
  if pattern in {'\\s','\\S','\\D','\\W', '\\w'}:
    whisper("Wildcard(s) not allowed because they are too broad. If you meant to seach plaintext use 's/[find]/[replace]' or delimit the wildcard (like s|\\\\s|!s", name, ircsock)
    return 
  # if new message would be over 200 characters then do not send.
  if len(new) > 200:
    whisper("Resulting message is too long (200 char max)", name, ircsock)
    return
  # if new message is empty string do not send.
  if len(new) == 0:
    whisper("Replace resulted in empty messge. Nothing to send", name, ircsock)
    return
  # if message isn't caught by one of the checks, send to channel and log the message.
  message="Correction, <" + name + ">: " + new
  sendmsg(message.strip('\r\n'), ircsock)
  logger(name, new, ircsock)

# send help message to users
def help(name,ircsock,topic=''):
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
  whisper(message, name, ircsock)
