import json
from datetime import datetime
from tickets.ticketsFinder import TicketsFinder
from .gameTicket import GameTicket
from .game import Game


class GameFinder(TicketsFinder):
    def __init__(self, infoUrl, lock):
        TicketsFinder.__init__(self, infoUrl, lock)        

    def jsonToTickets(self, ticketsJson):
        gamesJson = ticketsJson['Data']['PRODUCTIMT']
        availabilitiesJson = ticketsJson['Data']['Availability']
        games = []

        for game in gamesJson:
            tickets = []
            for availability in availabilitiesJson:
                if game['ProductId'] == availability['p']:
                    tickets.append(GameTicket(availability['c'], availability['a'] > 0))
            date = datetime.strptime(game['MatchDate'] , '%Y-%m-%dT%H:%M:%S')
            games.append(Game(game['ProductId'], game['ProductPublicName'], game['MatchStadium'], date, tickets))
        return games

    def getDate(self, variantMovement):
        date = datetime.strptime(variantMovement['date'] + ' 2018 ' + variantMovement['time'] , '%d %B %Y %H:%M')
        return date

    def findTickets(self):
        ticketsJson = TicketsFinder.findTickets(self)
        games = self.jsonToTickets(ticketsJson)
        return games

    def findAvailableTickets(self):
        games = self.findTickets()
        availableGames = []
        for game in games:
            for ticket in game.tickets:
                if ticket.isAvailable:
                    availableGames.append(game)
        return availableGames

    def getNewAvailableTickets(self):
        self.lock.acquire()

        currentAvailableTickets = self.findAvailableTickets()
        newAvailableTickets = []
        for availableTicket in currentAvailableTickets:
            if(all(availableTicket.id != ticket.id or availableTicket.freeSeats > ticket.freeSeats for ticket in self.alreadyFoundAvailableTickets)):
                newAvailableTickets.append(availableTicket)
        self.alreadyFoundAvailableTickets = currentAvailableTickets;

        self.lock.release()

        return newAvailableTickets

