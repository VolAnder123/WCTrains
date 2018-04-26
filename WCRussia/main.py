import datetime
import threading
import requests
import logging
from time import sleep
from botHandler import BotHandler
from trains.trainFinder import TrainFinder
from searchType import SearchType

bot = BotHandler('588416451:AAHeNyVIy_ARN9kmPhM62ARjNE1cwFFf5JE', '403996075') 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9"
                          , datetime.datetime(2018, 6, 15, 10), datetime.datetime(2018, 6, 16)
                          , datetime.datetime(2018, 6, 17, 7), datetime.datetime(2018, 6, 19, 17), threading.Lock())

def messageHandler():
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
                bot.sendMessage(last_chat_id, 'Сча узнаю. Пару сек')
                try:
                    responseText = GetFreeTrainsString()
                    if(responseText is None):
                        responseText = 'Да нету ничего. Работай давай'
                except requests.exceptions.ConnectionError:
                    responseText = 'Не могу достучаться до сервака с билетами. Попробуй еще раз чуть позже'
            elif lowerMessage == "пинг" or lowerMessage == "ping":
                responseText = "живой я"
            elif lowerMessage == "ты спортсмен?":
                responseText = 'иди нахуй'
            else:
                responseText = 'Я хз о чем ты'

            if responseText is not None:
                bot.sendMessage(last_chat_id, responseText)

            new_offset = last_update_id + 1


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
    freeTrains = trainFinder.getNewFreeTrains()
    if(len(freeTrains) > 0):
        responseText = ""
        for train in freeTrains:
            responseText += "Свободно: {0}\n".format(train.freeSeats)
        responseText += "https://tickets.transport2018.com/free-train/schedule"
    return responseText


def CheckGames():
    return 1


def main(searchType: SearchType): 
    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_TRAIN_TICKETS:
        trainsThread = threading.Thread(target = CheckTrains)
        trainsThread.start()

    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_GAME_TICKETS:
        gamesThread = threading.Thread(target = CheckGames)
        gamesThread.start()

    messageHandler()


if __name__ == '__main__':  
    try:
        main(SearchType.ONLY_TRAIN_TICKETS)
    except KeyboardInterrupt:
        exit()