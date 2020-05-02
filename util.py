def getPlayerNameInput(targetId: str, text: str = '') -> str:
	return input(text)

def getBidInput(targetId: str, text: str = '') -> str:
	return input(text)

def getPartnerInput(targetId: str, text: str = '') -> str:
	return input(text)

def getCardInput(targetId: str, text: str = '') -> str:
	return input(text)

def showText(text: str):
	print(text)

def showCards(player: dict):
	sortedReversedDeck = sorted(card['suit'] + card['num'] for card in player['hand'])
	text = ' '.join([rCard[1:] + rCard[0] for rCard in sortedReversedDeck])
    
	print(text)