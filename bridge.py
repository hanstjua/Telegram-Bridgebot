class table:
    def __init__(self):
        self.playedCards = {
            'N':'',
            'E':'',
            'S':'',
            'W':''
        }
        self.history = list()
        self.turnNo = len(self.history)

    def checkHist(self,turn=-1):
        if turn == -1:
            print(self.history)
        else:
            print(self.history[turn-1])

class scorer:
    def __init__(self):
        self.scores = list()

class turnTracker:
    pass

class player:
    def __init__(self, name, direction):
        self.name = name
        self.dir = direction
        self.hand = list()

    def getHand(self, deck):
        