from .gameTicketCategoryType import GameTicketCategoryType

class GameTicketCategory:
    def __init__(self, gameTicketCategoryType: GameTicketCategoryType, categoryName):
        self.gameTicketCategoryType = gameTicketCategoryType
        self.categoryName = categoryName