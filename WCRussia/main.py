import datetime
import threading
import requests
import logging
from time import sleep
from botHandler import BotHandler
from tickets.trains.trainFinder import TrainFinder
from tickets.games.gameFinder import GameFinder
from searchType import SearchType
from tickets.games.gameTicketCategoryType import GameTicketCategoryType
from tickets.games.stadiumType import StadiumType

bot = BotHandler('592870698:AAEu56VyOM8eAFthJSDFrQu-2wYOWb9AIHM', ['403996075'])#, '401655687']) 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9", threading.Lock()
                          , datetime.datetime(2018, 6, 15, 10), datetime.datetime(2018, 6, 16)
                          , datetime.datetime(2018, 6, 17, 7), datetime.datetime(2018, 6, 19, 17))
gameFinder = GameFinder("https://tickets.fifa.com/API/WCachedL1/ru/BasicCodes/GetBasicCodesAvailavilityDemmand?currencyId=USD", threading.Lock()
                        , [], [GameTicketCategoryType.CAT3], [], [StadiumType.SPB, StadiumType.MLU, StadiumType.MSP])

weekDays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс" ]

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
            if lowerMessage == "/checkall":
                bot.sendMessage(last_chat_id, 'Ищу билеты на поезда и матчи...')
                responseText = GetTicketsMessage(SearchType.EVERYTHING)
            elif lowerMessage in ["пинг", "ping", "/ping"]:
                responseText = "живой я"
            elif lowerMessage == "/checktrains":
                bot.sendMessage(last_chat_id, 'Ищу билеты на поезда...')
                responseText = GetTicketsMessage(SearchType.ONLY_TRAIN_TICKETS)
            elif lowerMessage in ["чпч", "/checkgames"]:
                bot.sendMessage(last_chat_id, 'Ищу билеты на матчи...')
                responseText = GetTicketsMessage(SearchType.ONLY_GAME_TICKETS)
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

def GetTicketsMessage(searchType: SearchType):
    trainsResponseText = None
    gamesResponseText = None
    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_TRAIN_TICKETS:
        try:
            trainsResponseText = GetFreeTrainsString(trainFinder.findAvailableTickets())
        except requests.exceptions.ConnectionError:
            trainsResponseText = 'Не могу достучаться до сервака с билетами на поезда. Попробуй еще раз чуть позже'
    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_GAME_TICKETS:
        try:
            gamesResponseText = GetFreeGamesString(gameFinder.findAvailableGames())
        except requests.exceptions.ConnectionError:
            gamesResponseText = 'Не могу достучаться до сервака с билетами на матчи. Попробуй еще раз чуть позже'
    responseText = joinStrings([trainsResponseText, gamesResponseText], "\n\n")
    if responseText is None:
        responseText = "Нету ничего"
    return responseText

def CheckTrains():
    try:
        while True:
            freeTrainsString = GetFreeTrainsString(trainFinder.getNewAvailableTickets())
            if freeTrainsString is not None:
                bot.sendMessageToAll(freeTrainsString)
            sleep(90)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')


def GetFreeTrainsString(freeTrains):
    responseText = None
    if(len(freeTrains) > 0):
        responseText = "Поезда:\n"
        for train in freeTrains:
            responseText += "Свободно: {0}\n".format(train.freeSeats)
        responseText += "https://tickets.transport2018.com/free-train/schedule"
    return responseText

def CheckGames():
    try:
        while True:
            freeGamesString = GetFreeGamesString(gameFinder.getNewAvailableGames())
            if freeGamesString is not None:
                bot.sendMessageToAll(freeGamesString)
            sleep(30)
    except requests.exceptions.ConnectionError:
        logging.warning('Connection refused')

def GetFreeGamesString(freeGames):
    responseText = None
    if(len(freeGames) > 0):
        responseText = "Матчи:"
        for game in freeGames:
            responseText += "\n{0}, {1}: ".format(weekDays[game.date.weekday()], game.name)
            for ticket in game.tickets:
                responseText += "{0}, ".format(ticket.gameTicketCategory.categoryName)
            responseText = responseText[:-2]
        responseText += "\nhttps://queue.tickets.fifa.com/?c=fifa&e=fwc2018&cid=ru-RU&t_lang=ru"
    return responseText


def main(): 
    searchType = SearchType.ONLY_GAME_TICKETS

    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_TRAIN_TICKETS:
        trainsThread = threading.Thread(target = CheckTrains)
        trainsThread.start()

    if searchType == SearchType.EVERYTHING or searchType == SearchType.ONLY_GAME_TICKETS:
        gamesThread = threading.Thread(target = CheckGames)
        gamesThread.start()

    messageHandler(searchType)


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()