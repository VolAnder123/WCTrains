from .gameTicketCategory import GameTicketCategory

class GameTicket:
    def __init__(self, gameTicketCategory: GameTicketCategory, isAvailable):
        self.gameTicketCategory = gameTicketCategory
        self.isAvailable = isAvailable