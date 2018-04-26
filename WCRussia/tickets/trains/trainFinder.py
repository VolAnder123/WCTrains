import json
from datetime import datetime
from .trainType import TrainType
from .train import Train
from tickets.ticketsFinder import TicketsFinder


class TrainFinder(TicketsFinder):
    def __init__(self, infoUrl, lock, minDepartureDateToTheGame, maxDepartureDateToTheGame, minArrivalDateFromTheGame, maxArrivalDateFromTheGame):
        TicketsFinder.__init__(self, infoUrl, lock)
        self.minDepartureDateToTheGame = minDepartureDateToTheGame
        self.maxDepartureDateToTheGame = maxDepartureDateToTheGame
        self.minArrivalDateFromTheGame = minArrivalDateFromTheGame
        self.maxArrivalDateFromTheGame = maxArrivalDateFromTheGame

    def jsonToTrain(self, trainsJson, trainType):
        variants = trainsJson['variants']
        trains = []
        for variant in variants:
            departureDate = self.getDate(variant['departure'])
            arrivalDate = self.getDate(variant['arrival'])
            trains.append(Train(variant['id'], variant['seats'], trainType, departureDate, arrivalDate))
        return trains

    def getDate(self, variantMovement):
        date = datetime.strptime(variantMovement['date'] + ' 2018 ' + variantMovement['time'] , '%d %B %Y %H:%M')
        return date

    def findTickets(self):
        trainsJson = TicketsFinder.findTickets(self)
        trains = self.jsonToTrain(trainsJson[0], TrainType.TO)
        trains.extend(self.jsonToTrain(trainsJson[1], TrainType.FROM))
        return trains

    def findFreeTrains(self):
        trains = self.findTickets()
        freeTrains = []
        for train in trains:
            if (train.freeSeats > 0) and (
                (train.trainType == TrainType.TO and train.departureDate >= self.minDepartureDateToTheGame and train.departureDate <= self.maxDepartureDateToTheGame) 
                or (train.trainType == TrainType.FROM and train.arrivalDate >= self.minArrivalDateFromTheGame and train.arrivalDate <= self.maxArrivalDateFromTheGame)):
                freeTrains.append(train)
        return freeTrains

    def getNewFreeTrains(self):
        self.lock.acquire()

        currentFreeTrains = self.findFreeTrains()
        newFreeTrains = []
        for freeTrain in currentFreeTrains:
            if(all(freeTrain.id != train.id or freeTrain.freeSeats > train.freeSeats for train in self.alreadyFoundAvailableTickets)):
                newFreeTrains.append(freeTrain)
        self.alreadyFoundAvailableTickets = currentFreeTrains;

        self.lock.release()

        return newFreeTrains

