import TS3
from TS3.utils import *


import re

import random

def randint(min, max):
	if randint.nerf:
		return min
	if randint.buff:
		return max
	return random.randint(min,max)

randint.buff = False
randint.nerf = False	
	
def baseconvert(n, base):
    """convert positive decimal integer n to equivalent in another base (2-36)"""

    digits = "0123456789abcdefghijklmnopqrstuvwxyz"

    try:
        n = int(n)
        base = int(base)
    except:
        return ""

    if n < 0 or base < 2 or base > 36:
        raise Exception()

    s = ""
    while 1:
        r = n % base
        s = digits[r] + s
        n = n / base
        if n == 0:
            break

    return s

dieRE = re.compile(r"([+-])?([0-9]+)d?([0-9]+)?")


def roll(die, sides):
	ret = []
	for x in xrange(die):
		ret.append(randint(1,sides))
	return ret
	
def asString(array):
	return [str(x) for x in array]

	
class DiceRolls:
	def __init__(self, rolls):
		self.sum = sum(rolls)
		self.rolls = [str(x) for x in rolls]
	def __str__(self):
		return "( %s )" % ",".join(self.rolls)
	def __repr__(self):
		return str(self)

class DieObject:
	def __init__(self, string):
		match = dieRE.match(string)
		if match.group(1) == "-":
			self.negative = True
		else:
			self.negative = False
		self.singular = False
		if match.group(3):
			self.die = int(match.group(2))
			self.sides = int(match.group(3))
		else:
			self.singular = True
			self.die = 1
			self.sides = int(match.group(2))
		if self.die > 1000:
			return "Error, too many die"
	def getRolls(self):
		if self.negative:
			return DiceRolls([-randint(1,self.sides) for x in xrange(self.die)])
		else:
			return DiceRolls([randint(1,self.sides) for x in xrange(self.die)])
	def getRaw(self):
		if self.negative:
			return -self.sides
		else:
			return self.sides
	def __repr__(self):
		return str(self)
	def __str__(self):
		return "n:%s,d:%s,s:%s" % (self.negative, self.die, self.sides)

PRIVLAGED_ID = "1SxxOJAwC0vWHWtMxxsGjU//rO4="

class RandomHandler(TS3.ClientEventHandler):
	
	def handleRoll(self, params):
		dice = []
		
		params = params.replace(" ","")
		
		if "+" not in params and "-" not in params:
			try:			
				roll = randint(1,int(params))
				return "( %s ) = %s" % (roll, roll)
			except ValueError:
				pass
		
		
		for x in dieRE.finditer(params):
			dice.append(DieObject(x.group(0)))
			
		if len(dice) == 0:
			roll = randint(1,20)
			return "( %s ) = %s" % (roll, roll)
		
		if len(dice) == 1 and dice[0].singular:
			roll = randint(1,20)
			return "( %s ) + %s = %s" % (roll, dice[0].getRaw(), roll + dice[0].getRaw())
		
		output = ""
		total = 0
		for x in dice:
			if x.singular:
				output += "%+d " % x.getRaw()
				total += x.getRaw()
			else:
				rolls = x.getRolls()
				output += str(rolls) + " "
				total += rolls.sum
		return "%s= %s" % (output, total)
		
	def parse_message(self, message, fromClient, privlaged = False):
		parts = message.split(" ")
		if parts[0] == "!roll":
			return self.handleRoll("".join(parts[1:]))
		if parts[0] == "!shuffle":
			if len(parts) == 2:
				seq = [x for x in parts[1]]
				random.shuffle(seq)
				return " ".join(seq)
			elif len(parts) > 2:
				seq = parts[1:]
				random.shuffle(seq)
				return " ".join(seq)
			else:
				return "Error incorrect format"
		if parts[0] == "!teams":
			if len(parts) == 2 and parts[1] == "all":
				clients = Client.get_all_clients(self.connection)
			else:
				clients = fromClient.get_channel().get_clients()
			clients = [c.get_name() for c in clients]
			random.shuffle(clients)
			odd = None
			if len(clients) % 2 == 1:
				odd = clients.pop()
			message = "\n[color=red]Team 1[/color]:\n%s\n[color=blue]Team 2[/color]:\n%s\n"
			message = message % ("\n".join(clients[0:len(clients)/2]),"\n".join(clients[len(clients)/2:]))
			if odd:
				message += "\n Odd person:%s" % odd
			return message
		if privlaged:
			if parts[0] == "!buff":
				randint.buff = True
				return "Rolls have been buffed"
			if parts[0] == "!nerf":
				randint.nerf = True
				return "Rolls have been nerfed"
			if parts[0] == "!balance":
				randint.nerf = False
				randint.buff = False
				return "Rolls have been balanced"

	def onTextMessageEvent(self, connection, message, targetMode, toID, fromID, **kwargs):
		fromClient = Client(connection, fromID)
		self.connection = connection
		message = self.parse_message(message, fromClient, fromClient.get_unique_identifier() == PRIVLAGED_ID)
		if message == None:
			return
		if targetMode == constants.TextMessageTargetMode.TextMessageTarget_CLIENT:
			fromClient.send_private_message(message)
		elif targetMode == constants.TextMessageTargetMode.TextMessageTarget_CHANNEL:
			connection.requestSendChannelTextMsg(message = message, targetChannelID = Client.get_self(connection).get_channel().channel_id, returnCode = "")
		elif targetMode == constants.TextMessageTargetMode.TextMessageTarget_SERVER:
			connection.requestSendServerTextMsg(message = message, returnCode = "")

		
		
TS3.register_callback_handler(RandomHandler())


