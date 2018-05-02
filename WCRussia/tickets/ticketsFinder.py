import requests
from abc import ABC, abstractmethod

class TicketsFinder(ABC):
    def __init__(self, infoUrl, lock):
        self.infoUrl = infoUrl
        self.lock = lock
        self.alreadyFoundAvailableTickets = []

    def findTickets(self):
        response = requests.get(self.infoUrl)
        return response.json()