import json
from datetime import datetime
from tickets.ticketsFinder import TicketsFinder
from .gameTicket import GameTicket
from .game import Game
from .gameTicketCategory import GameTicketCategory
from .gameTicketCategoryType import GameTicketCategoryType
from .stadium import Stadium
from .stadiumType import StadiumType


class GameFinder(TicketsFinder):
    def __init__(self, infoUrl, lock, rounds, categoryType, weekdays, stadiumTypes):
        TicketsFinder.__init__(self, infoUrl, lock)    
        self.rounds = rounds
        self.categoryType = categoryType
        self.weekdays = weekdays
        self.stadiumTypes = stadiumTypes

    def jsonToGames(self, ticketsJson):
        gamesJson = ticketsJson['Data']['PRODUCTIMT']
        availabilitiesJson = ticketsJson['Data']['Availability']
        categoriesJson = ticketsJson['Data']['CATEGORIES']
        stadiumsJson = ticketsJson['Data']['VENUES']
        games = []

        for game in gamesJson:
            if game['MatchIsClosed'] == False:
                tickets = []
                for availability in availabilitiesJson:
                    if game['ProductId'] == availability['p']:
                        isAvailable = availability['a'] > 0
                        tickets.append(GameTicket(self.getCategory(categoriesJson, availability['c']), isAvailable))
                date = datetime.strptime(game['MatchDate'] , '%Y-%m-%dT%H:%M:%S')
                games.append(Game(game['ProductId'], game['ProductPublicName']
                                  , self.getStadium(stadiumsJson, game['MatchStadium']), date, game['Rounds'], tickets))
        return games

    def getCategory(self, categoriesJson, categoryId):
        for category in categoriesJson:
            if categoryId == category['CategoryId']:
                return GameTicketCategory(GameTicketCategoryType(categoryId), category['CategoryNameOnTicket'])
        return None

    def getStadium(self, stadiumsJson, stadiumId):
        for stadium in stadiumsJson:
            if stadiumId == stadium['StadiumId']:
                return Stadium(StadiumType(stadiumId), stadium['StadiumName'])
        return None

    def findTickets(self):
        ticketsJson = TicketsFinder.findTickets(self)
        games = self.jsonToGames(ticketsJson)
        return games

    def findAvailableGames(self):
        games = self.findTickets()
        availableGames = []
        for game in games:
            if (not self.rounds or game.round in self.rounds) and (not self.weekdays or game.date.weekday() in self.weekdays) and game.stadium.stadiumType in self.stadiumTypes:
                availableTickets = []
                for ticket in game.tickets:
                    if ticket.isAvailable and ticket.gameTicketCategory.gameTicketCategoryType in self.categoryType:
                        availableTickets.append(ticket)
                if(len(availableTickets) > 0):
                    game.tickets = availableTickets
                    availableGames.append(game)
        return availableGames

    def getNewAvailableGames(self):
        self.lock.acquire()

        currentAvailableGames = self.findAvailableGames()
        newAvailableGames = []
        for currentAvailableGame in currentAvailableGames:
            alreadyFoundGame = next((ticket for ticket in self.alreadyFoundAvailableTickets if currentAvailableGame.id == ticket.id), None)
            if(alreadyFoundGame is None):
                newAvailableGames.append(currentAvailableGame)
            else:
                newAvailableTickets = []
                for currentAvailableTicket in currentAvailableGame.tickets:
                    isFound = False
                    for ticket in alreadyFoundGame.tickets:
                        if currentAvailableTicket.gameTicketCategory.gameTicketCategoryType == ticket.gameTicketCategory.gameTicketCategoryType:
                            isFound = True
                    if isFound == False:
                        newAvailableTickets.append(currentAvailableTicket)
                if(len(newAvailableTickets) > 0):
                    currentAvailableGame.tickets = newAvailableTickets
                    newAvailableGames.append(currentAvailableGame)
        self.alreadyFoundAvailableTickets = currentAvailableGames;

        self.lock.release()

        return newAvailableGames

