from tickets.entity import Entity

class Train(Entity):
    def __init__(self, id, freeSeats, trainType, departureDate, arrivalDate):
        Entity.__init__(self, id)
        self.freeSeats = freeSeats
        self.trainType = trainType
        self.departureDate = departureDate
        self.arrivalDate = arrivalDate
