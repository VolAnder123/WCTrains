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
    def __init__(self, infoUrl, lock):
        TicketsFinder.__init__(self, infoUrl, lock)        

    def jsonToGames(self, ticketsJson):
        gamesJson = ticketsJson['Data']['PRODUCTIMT']
        availabilitiesJson = ticketsJson['Data']['Availability']
        categoriesJson = ticketsJson['Data']['CATEGORIES']
        stadiumsJson = ticketsJson['Data']['VENUES']
        games = []

        for game in gamesJson:
            tickets = []
            for availability in availabilitiesJson:
                if game['ProductId'] == availability['p']:
                    #tickets.append(GameTicket(self.getCategory(categoriesJson, availability['c']), availability['a'] > 0))
                    tickets.append(GameTicket(self.getCategory(categoriesJson, availability['c']), True))
                    break
            date = datetime.strptime(game['MatchDate'] , '%Y-%m-%dT%H:%M:%S')
            games.append(Game(game['ProductId'], game['ProductPublicName'], self.getStadium(stadiumsJson, game['MatchStadium']), date, tickets))
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

    def findAvailableGames(self, categoryType, weekdays, stadiumTypes):
        games = self.findTickets()
        availableGames = []
        for game in games:
            if game.date.weekday() in weekdays and game.stadium.stadiumType in stadiumTypes:
                availableTickets = []
                for ticket in game.tickets:
                    if ticket.isAvailable and ticket.gameTicketCategory.gameTicketCategoryType in categoryType:
                        availableTickets.append(ticket)
                if(len(availableTickets) > 0):
                    game.tickets = availableTickets
                    availableGames.append(game)
        return availableGames

    def getNewAvailableGames(self):
        self.lock.acquire()

        currentAvailableGames = self.findAvailableGames([GameTicketCategoryType.CAT1, GameTicketCategoryType.CAT2, GameTicketCategoryType.CAT3, GameTicketCategoryType.CAT4],
                                                        [5,6],
                                                        [StadiumType.SPB, StadiumType.MLU, StadiumType.MSP])
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

