import TS3
from TS3.utils import *

import urllib2
import urllib
import json
import re

regex = re.compile(r"([a-zA-Z0-9-_]{11})")

url = "http://192.168.1.201:11163/request"

def play(youtube):
	query = url+"?action=add-song"
	query += "&%s=%s" % (urllib.quote("youtube-link"), urllib.quote(youtube))
	print query
	urllib2.urlopen(query)

def stop():
	urllib2.urlopen(url+"?action=clear")
def pause():
	urllib2.urlopen(url+"?action=stop")
def skip():
	urllib2.urlopen(url+"?action=skip")

titleRegex = re.compile(r"<title>(.*)</title>")
def getTitle(video):
	try:
		data = urllib2.urlopen("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % video)
		data = data.read()
		title = titleRegex.search(data).group(1)
		return title
	except:
		return ""
help = """
TeamSpeak Radio
!radio <command>

Commands:
help - Print this message
play - Start the radio if it is stopped
play <link> - Play a video
pause - Pause the radio
stop - Removes all songs from the playlist
skip - Skip current video
status - Get currently playing video
goto <channel> -  Move the radio
lobby - Move the radio to the lobby or back to the radio channel
radio - Return back to its own channel
return - Return back to its own channel
More options at [url=http://radio.wesleyluk.com/]http://radio.wesleyluk.com/[/url]
"""

LOBBY_CHANNEL_ID = 1

class RadioHandler(TS3.ClientEventHandler):
	def goto(self, connection, channel):
		channels = Channel.get_all_channels(connection)
		for c in channels:
			if c.get_name().find(channel) == 0:
				c.move_to_channel()
				return
		for c in channels:
			if c.get_name().find(channel) > -1:
				c.move_to_channel()
				return

	def parse_message(self, connection, message):

		parts = message.split(" ")
		if len(parts) == 0:
			return
		if parts[0] != "!radio":
			return
		if len(parts) == 1 or parts[1] == "help":
			return help

		if parts[1] == "play":
			if(len(parts) > 2):
				play(parts[2])
			else:
				skip()

		elif parts[1] == "stop":
			stop()
		elif parts[1] == "pause":
			pause()
		elif parts[1] == "skip":
			skip()
		elif parts[1] == "status":
			value = json.loads(urllib2.urlopen(url).read())
			for song in value['playlist']:
				if song['uid'] == value['now_playing']:
					return song['title']
		elif parts[1] == "goto" and len(parts) > 2:
			self.goto(connection, parts[2])
		elif parts[1] == "lobby":
			if Client.get_self(connection).get_channel().channel_id == LOBBY_CHANNEL_ID:
				self.goto(connection, "Channel Factory")
			else:
				Channel(connection, LOBBY_CHANNEL_ID).move_to_channel()
		elif parts[1] == "return" or parts[1] == "radio":
			self.goto(connection, "Channel Factory")

	def check_should_stop(self, connection):
		me = Client.get_self(connection)
		channel = me.get_channel()
		if len(channel.get_clients()) <= 1:
			stop()

	def onTextMessageEvent(self, connection, message, targetMode, toID, fromID, **kwargs):
		response = self.parse_message(connection, message)
		if response == None:
			return

		if targetMode == constants.TextMessageTargetMode.TextMessageTarget_CLIENT:
			fromClient.send_private_message(response)
		elif targetMode == constants.TextMessageTargetMode.TextMessageTarget_CHANNEL:
			connection.requestSendChannelTextMsg(message = response, targetChannelID = Client.get_self(connection).get_channel().channel_id, returnCode = "")
		elif targetMode == constants.TextMessageTargetMode.TextMessageTarget_SERVER:
			connection.requestSendServerTextMsg(message = response, returnCode = "")

	def onClientMoveEvent(self, connection, **kwargs):
		self.check_should_stop(connection)
	def onClientMoveMovedEvent(self, connection, **kwargs):
		self.check_should_stop(connection)


TS3.register_callback_handler(RadioHandler())
