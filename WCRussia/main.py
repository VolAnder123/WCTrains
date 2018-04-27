import datetime
import threading
import requests
import logging
from time import sleep
from botHandler import BotHandler
from tickets.trains.trainFinder import TrainFinder
from tickets.games.gameFinder import GameFinder
from searchType import SearchType

bot = BotHandler('588416451:AAHeNyVIy_ARN9kmPhM62ARjNE1cwFFf5JE', '403996075') 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9", threading.Lock()
                          , datetime.datetime(2018, 6, 15, 10), datetime.datetime(2018, 6, 16)
                          , datetime.datetime(2018, 6, 17, 7), datetime.datetime(2018, 6, 19, 17))
gameFinder = GameFinder("https://tickets.fifa.com/API/WCachedL1/ru/BasicCodes/GetBasicCodesAvailavilityDemmand?currencyId=USD", threading.Lock())

def messageHandler(searchType: SearchType):
    new_offset = None

    while True:
        last_update = bot.getLastUpdate(new_offset)

        if(last_update is not None):
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']

            lowerMessage = last_chat_text.lower()

            responseText = None
            if lowerMessage == "чпч":
                if searchType != SearchType.NOTHING:
                    bot.sendMessage(last_chat_id, 'Сча все узнаю. Пару сек')
                    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_TRAIN_TICKETS:
                        try:
                            trainsResponseText = GetFreeTrainsString()
                        except requests.exceptions.ConnectionError:
                            trainsResponseText = 'Не могу достучаться до сервака с билетами на поезда. Попробуй еще раз чуть позже'

                    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_GAME_TICKETS:
                        try:
                            gamesResponseText = GetFreeGamesString()
                        except requests.exceptions.ConnectionError:
                            gamesResponseText = 'Не могу достучаться до сервака с билетами на поезда. Попробуй еще раз чуть позже'
                    
                    responseText = joinStrings([trainsResponseText, gamesResponseText], "\n")
                    if responseText is None:
                        responseText = "Нету ничего"
                else:
                    responseText = "А как я пойму чего ты хочешь? Ты настроил так, чтобы я ничего не искал сам. Попробуй спросить подругому"
            elif lowerMessage in ["пинг", "ping", "/ping"]:
                responseText = "живой я"
            elif lowerMessage == "ты спортсмен?":
                responseText = 'иди нахуй'
            else:
                responseText = 'Я хз о чем ты'

            if responseText is not None:
                bot.sendMessage(last_chat_id, responseText)

            new_offset = last_update_id + 1

def joinStrings(stringArray, separator: str):
    response = None
    for string in stringArray:
        if(string is not None):
            if(response is not None):
                response += separator + string
            else:
                response = string
    return response

def CheckTrains():
    try:
        while True:
            freeTrainsString = GetFreeTrainsString()
            if freeTrainsString is not None:
                bot.sendMessageToAll(freeTrainsString)
            sleep(90)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')


def GetFreeTrainsString():
    responseText = None
    freeTrains = trainFinder.getNewAvailableTickets()
    if(len(freeTrains) > 0):
        responseText = ""
        for train in freeTrains:
            responseText += "Свободно: {0}\n".format(train.freeSeats)
        responseText += "https://tickets.transport2018.com/free-train/schedule"
    return responseText


def CheckGames():
    try:
        while True:
            freeGamesString = GetFreeGamesString()
            if freeGamesString is not None:
                bot.sendMessageToAll(freeGamesString)
            sleep(90)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')

def GetFreeGamesString():
    responseText = None
    freeTrains = gameFinder.getNewAvailableTickets()
    if(len(freeTrains) > 0):
        responseText = ""
        for train in freeTrains:
            responseText += "Свободно: {0}\n".format(train.freeSeats)
        responseText += "https://tickets.transport2018.com/free-train/schedule"
    return responseText


def main(): 
    searchType = SearchType.EVERYTHING

    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_TRAIN_TICKETS:
        trainsThread = threading.Thread(target = CheckTrains)
        #trainsThread.start()

    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_GAME_TICKETS:
        gamesThread = threading.Thread(target = CheckGames)
        gamesThread.start()

    messageHandler(searchType)


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()