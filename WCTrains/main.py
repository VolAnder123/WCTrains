import datetime
import threading
import requests
import logging
from time import sleep
from botHandler import BotHandler
from trainFinder import TrainFinder

bot = BotHandler('588416451:AAHeNyVIy_ARN9kmPhM62ARjNE1cwFFf5JE', '403996075') 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9"
                          , datetime.datetime(2018, 6, 15, 10), datetime.datetime(2018, 6, 16)
                          , datetime.datetime(2018, 6, 17, 7), datetime.datetime(2018, 6, 17, 17), threading.Lock())

def DisplayFreeTrains():
    freeTrains = trainFinder.getNewFreeTrains()
    if(len(freeTrains) > 0):
        responseText = ""
        for train in freeTrains:
            responseText += "Свободно: {0}\n".format(train.freeSeats)
        responseText += "https://tickets.transport2018.com/free-train/schedule"
        SendMessage(bot.getAllChatIds(), responseText)
        return True
    else:
        return False
    return 

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
                    if(DisplayFreeTrains() == False):
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
            DisplayFreeTrains()
            sleep(90)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')

def SendMessage(chatIds, message):
    for chatId in chatIds:
        bot.sendMessage(chatId, message)


def main(): 
    thread = threading.Thread(target = CheckTrains)
    thread.start()

    messageHandler()


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()