import json
from datetime import datetime
from tickets.ticketsFinder import TicketsFinder
from .gameTicket import GameTicket
from .game import Game
from .gameTicketCategory import GameTicketCategory
from .gameTicketCategoryType import GameTicketCategoryType


class GameFinder(TicketsFinder):
    def __init__(self, infoUrl, lock):
        TicketsFinder.__init__(self, infoUrl, lock)        

    def jsonToGames(self, ticketsJson):
        gamesJson = ticketsJson['Data']['PRODUCTIMT']
        availabilitiesJson = ticketsJson['Data']['Availability']
        categoriesJson = ticketsJson['Data']['CATEGORIES']
        games = []

        for game in gamesJson:
            tickets = []
            for availability in availabilitiesJson:
                if game['ProductId'] == availability['p']:
                    for category in categoriesJson:
                        if availability['c'] == category['CategoryId']:
                            tickets.append(GameTicket(GameTicketCategory(GameTicketCategoryType(availability['c']), category['CategoryNameOnTicket']), availability['a'] > 0))
                            break
            date = datetime.strptime(game['MatchDate'] , '%Y-%m-%dT%H:%M:%S')
            games.append(Game(game['ProductId'], game['ProductPublicName'], game['MatchStadium'], date, tickets))
        return games

    def findTickets(self):
        ticketsJson = TicketsFinder.findTickets(self)
        games = self.jsonToGames(ticketsJson)
        return games

    def findAvailableGames(self, categories):
        games = self.findTickets()
        availableGames = []
        for game in games:
            availableTickets = []
            for ticket in game.tickets:
                if ticket.isAvailable and ticket.gameTicketCategory.gameTicketCategoryType in categories:
                    availableTickets.append(ticket)
            if(len(availableTickets) > 0):
                game.tickets = availableTickets
                availableGames.append(game)
        return availableGames

    def getNewAvailableGames(self):
        self.lock.acquire()

        currentAvailableGames = self.findAvailableGames([GameTicketCategoryType.CAT1, GameTicketCategoryType.CAT2, GameTicketCategoryType.CAT3, GameTicketCategoryType.CAT4])
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

