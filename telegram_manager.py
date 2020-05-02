from bot_data import token

from enum import Enum

from stateless_bridge import main as bridgeMain

from telepot import Bot, DelegatorBot, glance
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.helper import ChatHandler
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from threading import Thread

from typing import Dict, List

import time

bot = None
messageBuffer = []

CHAR_TO_ESCAPE_LIST = ['(', ')', '.', '=']


class BotCommand(Enum):
	START = '/bridge'
	NAME = '/player'
	BID = '/bid'
	PARTNER = '/partner'
	CARD = '/'
	HELP = '/help'

STARTING_TEXT = '''Welcome to Lazy Bridge Bot!
Inputs to this bot are to be entered using the following syntax:
  /<COMMAND> <SPACE> <VALUE>

Command list:
{start} - Start a game
{name} - Enter a player's name
{bid} - Enter bid
{partner} - Enter partner of choice
{card} - Enter card to be played

Bid value is to be constructed using the following pattern:
  <BID LEVEL><SUIT>
  where BID LEVEL = no. 1-7
Examples: 1C, 2D, 3H, 4S, 5NT

Partner and card value is to be constructed using the following pattern:
  <CARD NUM><SUIT>
  where CARD NUM = 2, 3, ... J, Q, K, A
Examples: 2C, 10D, KH, AS

When card inputs are necessary, card buttons showing your current hand will be available to you. You can use these buttons to play your card.
'''.format(
	start=BotCommand.START.value,
	name=BotCommand.NAME.value,
	bid=BotCommand.BID.value,
	partner=BotCommand.PARTNER.value,
	card=BotCommand.CARD.value
	)


class TelegramManager(ChatHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bridgeThread: Thread = None

		self.messageBuffer: List[dict] = list()
		self.playerIdList: List[int] = list()
		self.chatIdMap: Dict[str, int] = dict()
		self.nameMap: Dict[str, str] = dict()

	def startBridgeThread(self):
		bridgeArgs = (
			self.getPlayerNameInput, 
			self.getBidInput, 
			self.getPartnerInput, 
			self.getCardInput, 
			self.showText, 
			self.showCards,
			)

		self.bridgeThread = Thread(target=bridgeMain, args=bridgeArgs)
		self.bridgeThread.start()

	def sanitiseString(self, string: str) -> str:
		for char in CHAR_TO_ESCAPE_LIST:
			string = string.replace(char, '\\' + char)

		return string

	def charToEmoji(self, string: str) -> str:
		return string.replace('C', '♣️').replace('D', '♦️').replace('H', '♥️').replace('S', '♠️')

	def charFromEmoji(self, string: str) -> str:
		return string.replace('♣️', 'C').replace('♦️', 'D').replace('♥️', 'H').replace('♠️', 'S')

	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = glance(msg)

		try:
			command = msg['text'].strip().lower()
		except KeyError:
			# ignore non-text messages
			return

		if command == BotCommand.START.value:
			if self.bridgeThread:
				self.sender.sendMessage("A game is still running!")
			else:
				self.chatId = chat_id
				self.sender.sendMessage(STARTING_TEXT)
				self.startBridgeThread()
		else:
			self.messageBuffer.append(msg)
			print('appended msg')
		

	def getPlayerNameInput(self, targetId: str, text: str = '') -> str:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')

		text = self.sanitiseString(text)
		self.sender.sendMessage(text)

		while True:
			if self.messageBuffer:
				message = self.messageBuffer.pop(0)	
				commandArgs = message['text'].strip().split(' ')
				if commandArgs[0] == BotCommand.NAME.value:
					self.chatIdMap[targetId] = message['from']['id']

					try:
						name = ' '.join(commandArgs[1:])
						self.nameMap[targetId] = name
					except IndexError:
						continue

					break

			time.sleep(0.01)

		return name

	def getBidInput(self, targetId: str, text: str = '') -> str:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')
		warning = r'Card buttons are to display your hand only. DO NOT PRESS ANY OF THE CARD BUTTONS.'
		text += '\n' + warning
		text = self.sanitiseString(text)

		bidMessage = '[{}](tg://user?id={}) '.format(self.nameMap[targetId], self.chatIdMap[targetId]) + text
		self.sender.sendMessage(bidMessage, parse_mode='MarkdownV2')

		bidInput = ''

		while True:
			if self.messageBuffer:
				message = self.messageBuffer.pop(0)

				if message['from']['id'] == self.chatIdMap[targetId]:
					commandArgs = message['text'].strip().split(' ')
					if commandArgs[0] == BotCommand.BID.value:
						try:
							bidInput = commandArgs[1]
						except IndexError:
							continue

						break

			time.sleep(0.01)

		return bidInput

	def getPartnerInput(self, targetId: str, text: str = '') -> str:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')

		text = self.sanitiseString(text)

		partnerMessage = '[{}](tg://user?id={}) '.format(self.nameMap[targetId], self.chatIdMap[targetId]) + text
		self.sender.sendMessage(partnerMessage, parse_mode='MarkdownV2')

		partnerInput = ''

		while True:
			if self.messageBuffer:
				message = self.messageBuffer.pop(0)

				if message['from']['id'] == self.chatIdMap[targetId]:
					commandArgs = message['text'].strip().split(' ')
					if commandArgs[0] == BotCommand.PARTNER.value:
						try:
							partnerInput = commandArgs[1]
						except IndexError:
							continue

						break

		return partnerInput

	def getCardInput(self, targetId: str, text: str = '') -> str:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')

		print('entered card input')

		text = self.sanitiseString(text)

		playMessage = '[{}](tg://user?id={}) '.format(self.nameMap[targetId], self.chatIdMap[targetId]) + text
		self.sender.sendMessage(playMessage, parse_mode='MarkdownV2')

		cardInput = ''

		print('entering loop ...')
		while True:
			print('loop')
			if self.messageBuffer:
				print('buffer check passed')
				message = self.messageBuffer.pop(0)
				print(message)

				if message['from']['id'] == self.chatIdMap[targetId]:
					commandArgs = message['text'].strip().split(' ')
					print(commandArgs)
					if commandArgs[0] == BotCommand.CARD.value:
						try:
							cardInput = commandArgs[1]
							cardInput = self.charFromEmoji(cardInput)
						except IndexError:
							print("indexError raised")
							continue

						print("exiting loop ...")
						break

			time.sleep(0.01)

		return cardInput

	def showText(self, text: str = '') -> None:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')

		self.sender.sendMessage(text)

	def showCards(self, player: dict) -> None:
		if not self.bridgeThread.is_alive():
			self.sender.sendMessage('bridge thread stopped ...')
		playerId = self.chatIdMap[player['side']]

		sortedReversedDeck = sorted(card['suit'] + card['num'] for card in player['hand'])
		handStr = '_'.join([BotCommand.CARD.value + ' ' + rCard[1:] + rCard[0] for rCard in sortedReversedDeck])
		handStr = self.charToEmoji(handStr)
		newHand = handStr.split('_')

		keyboardButtons = [
		[newHand[i] for i in range(min(len(newHand), 6))], 
		[newHand[i+6] for i in range(len(newHand) - 6)]
		]
		keyboard = ReplyKeyboardMarkup(keyboard=keyboardButtons, resize_keyboard=True, one_time_keyboard=True, selective=True)

		self.sender.sendMessage('Display [{}](tg://user?id={}) hand\.'.format(player['name'], playerId), parse_mode='MarkdownV2', reply_markup=keyboard)

def main():
	bot = DelegatorBot(token, [ pave_event_space()(per_chat_id(types=['group']), create_open, TelegramManager, timeout=300) ])
	MessageLoop(bot).run_as_thread()

	while 1:
		time.sleep(10)

if __name__ == '__main__':
	# todo:
	# reply keyboard button text and message text to be different

	main()
	pass


