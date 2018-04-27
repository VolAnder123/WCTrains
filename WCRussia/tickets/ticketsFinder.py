import requests
from abc import ABC, abstractmethod

class TicketsFinder(ABC):
    def __init__(self, infoUrl, lock):
        self.infoUrl = infoUrl
        self.lock = lock
        self.alreadyFoundAvailableTickets = []

    @abstractmethod
    def jsonToTickets(self, ticketsJson):
        pass

    def findTickets(self):
        response = requests.get(self.infoUrl)
        return response.json()
    
    @abstractmethod
    def findAvailableTickets(self):
        pass

    @abstractmethod
    def getNewAvailableTickets(self):
        pass
