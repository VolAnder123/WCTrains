from tickets.entity import Entity

class Game(Entity):
    def __init__(self, id, name, stadiumId, date, tickets):
        Entity.__init__(self, id)
        self.name = name
        self.stadiumId = stadiumId
        self.date = date
        self.tickets = tickets

