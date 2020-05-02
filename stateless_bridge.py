import math
import random
from enum import Enum
from typing import Tuple, Dict, Callable

from telepot import Bot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from bot_data import token

import util

bot = Bot(token)

def chatHandle(msg):
    print('text',msg)
    chat_id = msg['chat']['id']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me to play ♠️♥️♦️♣️', callback_data='press')],
               ])

    bot.sendMessage(chat_id, 'Your Turn', reply_markup=keyboard)

def callbackHandle(msg):
    print('callback:',msg)
    chat_id = msg['message']['chat']['id']
    
    keyboard = ReplyKeyboardMarkup(keyboard=[['/ ' + str(i+1) + '♦️' for i in range(random.randint(1,13))]], resize_keyboard=True, one_time_keyboard=True, selective=True)

    bot.sendMessage(chat_id, 'Example spades [{}](tg://user?id={})'.format(msg['from']['first_name'], msg['from']['id']), parse_mode='MarkdownV2', reply_markup=keyboard)

def createPlayer(name, hand, side):
    return {'name': name, 'hand': hand, 'side': side}

def createPlayerList(deck, getPlayerNameInput: Callable):
    sideList = ('N','E','S','W')

    return tuple([
        createPlayer(
            getPlayerNameInput(sideList[i], 'Enter name for {}: '.format(sideList[i])),
            deck[i*13:(i*13)+13],
            sideList[i]
            )
        for i in range(len(sideList))
        ])

def getValidBids() -> Dict[str, int]:
    bidNames = ['P'] + [str(n+1) + s for n in range(7) for s in ['C','D','H','S','NT']]
    
    return {bidNames[i]: i for i in range(len(bidNames))}

def getNextPlayerIndex(curIdx) -> int:
    if curIdx + 1 > 3:
        return 0
    else:
        return curIdx + 1

def getPlayerIndex(player: dict, playerList: Tuple[dict]) -> int:
    for i, p in enumerate(playerList):
        if player['side'] == p['side']:
            return i

    raise Exception('Unable to find player index.')

def progressBidPhase(curBid, curBidOwnerIdx, curPlayerIdx, playerList, getBidInput: Callable, showText: Callable) -> Tuple[str, dict]:
    if curPlayerIdx == curBidOwnerIdx:
        winner = playerList[curBidOwnerIdx]
        showText('Winning Bid: {}, Bid Winner: {}'.format(curBid, winner['name']))
        return curBid, winner
    else:
        if curBidOwnerIdx is not None:
            curBidOwner = playerList[curBidOwnerIdx]
            showText('Current Bid: {}, Bid Owner: {}'.format(curBid, curBidOwner['name']))
        validBids = getValidBids()
        curPlayer = playerList[curPlayerIdx]
        nextBid = getBidInput(curPlayer['side'], 'Please enter your bid: ').upper()

        # pass
        if nextBid == 'P':
            return progressBidPhase(
                curBid,
                curBidOwnerIdx,
                getNextPlayerIndex(curPlayerIdx),
                playerList,
                getBidInput,
                showText
                )
        # invalid bid
        elif not nextBid in validBids or validBids[nextBid] <= validBids[curBid]:
            showText('Invald bid entered.')
            return progressBidPhase(
                curBid,
                curBidOwnerIdx,
                curPlayerIdx,
                playerList,
                getBidInput,
                showText
                )
        # valid bid
        else:
            return progressBidPhase(
                nextBid,
                curPlayerIdx,
                getNextPlayerIndex(curPlayerIdx),
                playerList,
                getBidInput,
                showText
                )
            
def startBidPhase(playerList, bidOpenerIdx, getBidInput: Callable, showText: Callable) -> Tuple[str, dict]:
    showText('--- BID PHASE ---')
    return progressBidPhase('P', None, bidOpenerIdx, playerList, getBidInput, showText)

def progressPartneringPhase(bidWinner, chosenPartner, playerList, getPartnerInput: Callable, showText: Callable) -> dict:
    if chosenPartner is not None:
        return chosenPartner
    else:
        partnerCard = getPartnerInput(bidWinner['side'], 'Please choose your partner (eg. 2C, AD): ').upper()

        for player in playerList:
            if player['side'] == bidWinner['side']:
                continue
            
            for card in player['hand']:
                try:
                    if partnerCard[-1] == card['suit'] and partnerCard[:-1] == card['num']:
                        showText("{}'s partner is {}.".format(bidWinner['name'], partnerCard))
                        return progressPartneringPhase(bidWinner, player, playerList, getPartnerInput, showText)
                except:
                    showText('Invalid card entered.')
                    return progressPartneringPhase(bidWinner, chosenPartner, playerList, getPartnerInput, showText)

        showText('404 partner not found.')
        return progressPartneringPhase(bidWinner, chosenPartner, playerList, getPartnerInput, showText)

def startPartneringPhase(bidWinner, playerList, getPartnerInput: Callable, showText: Callable) -> Dict[str, Tuple[int]]:
    showText('--- PARTNERING PHASE ---')
    chosenPartner = progressPartneringPhase(bidWinner, None, playerList, getPartnerInput, showText)

    declarerPartners = tuple([getPlayerIndex(bidWinner, playerList), getPlayerIndex(chosenPartner, playerList)])
    defenderPartners = tuple([i for i in range(4) if i not in declarerPartners])

    return {'declarer': declarerPartners, 'defender': defenderPartners}

def showPlayerHand(player, showCards):
    showCards(player)

def getPlayCard(cardStr: str, player: dict) -> dict or None:
    for card in player['hand']:
        if card['num'] == cardStr[:-1] and card['suit'] == cardStr[-1]:
            return card
    return None

def getUpdatedPlayer(player, curPlayer, curPlayCard) -> dict:
    if player['side'] != curPlayer['side']:
        return player
    else:
        newHand = tuple([card for card in player['hand']
                         if not (card['num'] == curPlayCard['num']
                         and card['suit'] == curPlayCard['suit'])])

        return createPlayer(player['name'], newHand, player['side'])

def getUpdatedPlayerList(curPlayer, curPlayCard, playerList) -> Tuple[dict]:
    return tuple([getUpdatedPlayer(player, curPlayer, curPlayCard) for player in playerList])

def getNewWinningCardAndPlayerIndex(curWinningCard, curPlayCard, trumpSuit, curPlayerIdx, curWinnerIdx, showText: Callable) -> Tuple[Tuple[dict], int]:
    if curWinningCard:
        if curPlayCard['suit'] == trumpSuit:
            if curWinningCard['suit'] != trumpSuit or curPlayCard['value'] > curWinningCard['value']:
                return curPlayCard, curPlayerIdx
                showText('round1')
            else:
                return curWinningCard, curWinnerIdx
                showText('round2')
        elif curPlayCard['suit'] == curWinningCard['suit']:
            if curPlayCard['value'] > curWinningCard['value']:
                return curPlayCard, curPlayerIdx
                showText('round3')
            else:
                return curWinningCard, curWinnerIdx
                showText('round4')
        else:
            return curWinningCard, curWinnerIdx
            showText('round5')
    else:
        return curPlayCard, curPlayerIdx
        showText('round6')

def checkHandForNonTrumpValidPlay(curPlayer, startingSuit):
    for card in curPlayer['hand']:
        if card['suit'] == startingSuit:
            return True
    return False

def progressRound(starterIdx: int, startingSuit: str, curPlayerIdx: int,
    curWinnerIdx: int, curWinningCard: dict, trumpSuit: str,
    trumpIsBroken: bool, playerList: Tuple[dict], getCardInput: Callable, 
    showText: Callable, showCards: Callable) -> Tuple[int, bool, Tuple[dict]]:
    
    if curWinnerIdx is not None and curPlayerIdx == starterIdx:
        winningPlay = curWinningCard['num'] + curWinningCard['suit']
        winnerName = playerList[curWinnerIdx]['name']
        winnerSide = playerList[curWinnerIdx]['side']
        showText('>>> Round winner is {}'.format(winnerName))
        
        return curWinnerIdx, trumpIsBroken, playerList
    else:
        curPlayer = playerList[curPlayerIdx]
        showPlayerHand(curPlayer, showCards)
        curPlayStr = getCardInput(curPlayer['side'], "Please enter card to play: ").upper()

        curPlayCard = getPlayCard(curPlayStr, curPlayer)
        if not curPlayCard:
            showText('Invalid play.')
            return progressRound(
                starterIdx, 
                startingSuit, 
                curPlayerIdx, 
                curWinnerIdx, 
                curWinningCard, 
                trumpSuit, 
                trumpIsBroken, 
                playerList,
                getCardInput,
                showText,
                showCards
                )

        if curPlayCard['suit'] == trumpSuit:
            if not startingSuit and not trumpIsBroken:
                showText('Trump has not been broken.')
                return progressRound(
                    starterIdx,
                    startingSuit, 
                    curPlayerIdx, 
                    curWinnerIdx, 
                    curWinningCard, 
                    trumpSuit, 
                    trumpIsBroken, 
                    playerList,
                    getCardInput,
                    showText,
                    showCards
                    )
            elif startingSuit != trumpSuit:
                hasNonTrumpPlay = checkHandForNonTrumpValidPlay(curPlayer, startingSuit)
                if hasNonTrumpPlay:
                    showText('Please play non-trump card.')
                    return progressRound(
                        starterIdx,
                        startingSuit, 
                        curPlayerIdx, 
                        curWinnerIdx, 
                        curWinningCard, 
                        trumpSuit, 
                        trumpIsBroken, 
                        playerList,
                        getCardInput,
                        showText,
                        showCards
                        )

        if not startingSuit:
            newStartingSuit = curPlayCard['suit']
        else:
            newStartingSuit = startingSuit
        
        newWinningCard, newWinnerIdx = getNewWinningCardAndPlayerIndex(curWinningCard, curPlayCard, trumpSuit, curPlayerIdx, curWinnerIdx, showText)

        newPlayerList = getUpdatedPlayerList(curPlayer, curPlayCard, playerList)
        newPlayerIdx = getNextPlayerIndex(curPlayerIdx)

        try:
            newTrumpIsBroken = (newWinningCard['suit'] == trumpSuit) or trumpIsBroken
        except TypeError:
            newTrumpIsBroken = trumpIsBroken
        
        return progressRound(
            starterIdx, 
            newStartingSuit, 
            newPlayerIdx, 
            newWinnerIdx, 
            newWinningCard, 
            trumpSuit, 
            newTrumpIsBroken, 
            newPlayerList,
            getCardInput,
            showText,
            showCards
            )                   

def startRound(starterIdx, trumpSuit, trumpIsBroken, playerList, getCardInput: Callable, showText: Callable, showCards: Callable) -> Tuple[int, bool, Tuple[dict]]:
    return progressRound(starterIdx, None, starterIdx, None, None, trumpSuit, trumpIsBroken, playerList, getCardInput, showText, showCards)
                 
def progressGamePhase(roundNum, indivScores, curPlayerIdx, trumpSuit, trumpIsBroken, partners, declarerScore, defenderScore, declarerGoal, defenderGoal, playerList, getCardInput, showText, showCards) -> Tuple[int, int]:
    if declarerScore == declarerGoal:
        return partners['declarer']
    elif defenderScore == defenderGoal:
        return partners['defender']
    else:
        showText('--- ROUND {} ---\nSCORES: {}'.format(roundNum, indivScores))
        roundWinnerIdx, newTrumpIsBroken, newPlayerList = startRound(curPlayerIdx, trumpSuit, trumpIsBroken, playerList, getCardInput, showText, showCards)

        if roundWinnerIdx in partners['declarer']:
            newDeclarerScore = declarerScore + 1
            newDefenderScore = defenderScore
        elif roundWinnerIdx in partners['defender']:
            newDeclarerScore = declarerScore
            newDefenderScore = defenderScore + 1

        newIndivScores = tuple([indivScores[i] + 1 if i == roundWinnerIdx else indivScores[i] for i in range(4)])

        #print('scores: {} {}'.format(newDeclarerScore, newDefenderScore))
            
        return progressGamePhase(roundNum + 1, newIndivScores, roundWinnerIdx, trumpSuit, newTrumpIsBroken, partners, newDeclarerScore, newDefenderScore, declarerGoal, defenderGoal, newPlayerList, getCardInput, showText, showCards)

def startGamePhase(bidWinnerIdx, trumpSuit, partners, declarerGoal, defenderGoal, playerList, getCardInput: Callable, showText: Callable, showCards: Callable) -> Tuple[int, int]:
    showText('--- GAME PHASE ---')
    return progressGamePhase(1, tuple([0,0,0,0]), bidWinnerIdx, trumpSuit, False, partners, 0, 0, declarerGoal, defenderGoal, playerList, getCardInput, showText, showCards)

def accumulatePoint(curPoint, remainingHand, pointMap):
    suit = remainingHand[0]['num']
    newPoint = curPoint + pointMap.get(suit, 0)

    if len(remainingHand) == 1:
        return newPoint
    else:
        return accumulatePoint(newPoint, remainingHand[1:], pointMap)
    
def getHandPoints(hand):
    pointMap = {'J': 1, 'Q': 2, 'K': 3, 'A': 4}

    return accumulatePoint(0, hand, pointMap)
    
def getShuffledDeck(deck):
    randomizer = (random.sample(range(52), 52))
    shuffledDeck = tuple([deck[i] for i in randomizer])

    for i in range(4):
        hand = shuffledDeck[i*13:(i*13)+13]
        if getHandPoints(hand) < 4:
            return getShuffledDeck(shuffledDeck)

    return shuffledDeck

def getSortedDeck():
    return tuple(
        {'value': v, 'num': n, 'suit': s}
        for v, n in zip(range(13),
                        [str(i) for i in range(2,11,1)] + ['J','Q','K','A'])
        for s in ['C','D','H','S']
        )

def getGoals(winningBid) -> Tuple[int, int]:
    declarerGoal = 6 + int(winningBid[0])
    defenderGoal = 14 - declarerGoal

    return declarerGoal, defenderGoal

def main(getPlayerNameInput: Callable, getBidInput: Callable, getPartnerInput: Callable, getCardInput: Callable, showText: Callable, showCards: Callable):
    pList = createPlayerList(getShuffledDeck(getSortedDeck()), getPlayerNameInput)

    for p in pList:
        showPlayerHand(p, showCards)
        
    bidOpenerIdx = random.randint(0,3)
        
    winningBid, bidWinner = startBidPhase(pList, bidOpenerIdx, getBidInput, showText)
    bidWinnerIdx = getPlayerIndex(bidWinner, pList)
    openerIdx = getNextPlayerIndex(bidWinnerIdx)
    trumpSuit = winningBid[-1]
    print('win bid: {}, trump: {}'.format(winningBid, trumpSuit))
    partners = startPartneringPhase(bidWinner, pList, getPartnerInput, showText)
    declarerGoal, defenderGoal = getGoals(winningBid)
    print('goals: {} {}'.format(declarerGoal, defenderGoal))
    winningPartners = startGamePhase(openerIdx, trumpSuit, partners, declarerGoal, defenderGoal, pList, getCardInput, showText, showCards)

    winnerName1 = pList[winningPartners[0]]['name']
    winnerName2 = pList[winningPartners[1]]['name']
    showText('Winners are {} and {}. Congrats!'.format(winnerName1, winnerName2))

def test_telepot():
    routingTable = {
            'chat': chatHandle,
            'callback_query': callbackHandle,
        }
    MessageLoop(bot, routingTable).run_as_thread()

if __name__ == '__main__':
    main(util.getPlayerNameInput, util.getBidInput, util.getPartnerInput, util.getCardInput, util.showText, util.showCards)
    #test_telepot()
    while 1:
        pass

    # TODO:
    # check for 4 consecutive passes during bidding (?)
    # integrate with telegram
