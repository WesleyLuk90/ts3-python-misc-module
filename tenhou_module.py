import TS3

class TenhouModuleHandler(TS3.ClientEventHandler):
	def onTextMessageEvent(self, connection, message, **kwargs):
		if message.lower() == "!t":
			connection.requestSendServerTextMsg(message = "[url=http://tenhou.net/0/?3362]Tenhou[/url]", returnCode = "")

TS3.register_callback_handler(TenhouModuleHandler())