import datetime
import threading
import requests
import logging
from botHandler import BotHandler
from train import Train
from trainFinder import TrainFinder
from time import sleep

bot = BotHandler('588416451:AAHeNyVIy_ARN9kmPhM62ARjNE1cwFFf5JE') 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9", datetime.datetime(2018, 6, 15), datetime.datetime(2018, 6, 17, 22), threading.Lock())

def messageHandler():
    new_offset = None

    while True:
        last_update = bot.get_last_update(new_offset)

        if(last_update is not None):
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']

            lowerMessage = last_chat_text.lower()

            if lowerMessage == "чпч":
                bot.send_message(last_chat_id, 'Сча узнаю. Пару сек')
                try:
                    if(trainFinder.isFoundNewFreeTrains()):
                        responseText = 'Есть места!\nhttps://tickets.transport2018.com/free-train/schedule'
                    else:
                        responseText = 'Да нету ничего. Работай давай'
                except requests.exceptions.ConnectionError:
                    responseText = 'Не могу достучаться до сервака с билетами. Попробуй еще раз чуть позже'
            elif lowerMessage == "пинг" or lowerMessage == "ping":
                responseText = "живой я"
            elif lowerMessage == "ты спортсмен?":
                responseText = 'иди нахуй'
            else:
                responseText = 'Я хз о чем ты'

            bot.send_message(last_chat_id, responseText)

            new_offset = last_update_id + 1


def CheckTrains():
    try:
        while True:
            if(trainFinder.isFoundNewFreeTrains()):
                chatIds = bot.getAllChatIds()
                SendMessage(chatIds, 'Э, ебанько, там свободные места есть!\nhttps://tickets.transport2018.com/free-train/schedule')

            sleep(90)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')

def SendMessage(chatIds, message):
    for chatId in chatIds:
        bot.send_message(chatId, message)


def main(): 
    thread = threading.Thread(target = CheckTrains)
    thread.start()

    messageHandler()


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()