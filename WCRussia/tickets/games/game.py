from tickets.entity import Entity

class Game(Entity):
    def __init__(self, id, name, stadium, date, tickets):
        Entity.__init__(self, id)
        self.name = name
        self.stadium = stadium
        self.date = date
        self.tickets = tickets

