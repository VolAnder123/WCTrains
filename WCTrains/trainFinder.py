import requests
import json
from datetime import datetime
from trainType import TrainType
from train import Train

class TrainFinder:
    def __init__(self, gameUrl, minDepartureDateToTheGame, maxArrivalDateFromTheGame, lock):
        self.gameUrl = gameUrl
        self.minDepartureDateToTheGame = minDepartureDateToTheGame
        self.maxArrivalDateFromTheGame = maxArrivalDateFromTheGame
        self.lock = lock
        self.alreadyFoundFreeTrains = []

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

    def findTrains(self):
        response = requests.get(self.gameUrl)
        trainsJson = response.json()
        trains = self.jsonToTrain(trainsJson[0], TrainType.TO)
        trains.extend(self.jsonToTrain(trainsJson[1], TrainType.FROM))
        return trains

    def findFreeTrains(self):
        trains = self.findTrains()
        freeTrains = []
        for train in trains:
            if (train.freeSeats > 0) and ((train.trainType == TrainType.TO and train.departureDate >= self.minDepartureDateToTheGame) or (train.trainType == TrainType.FROM and train.arrivalDate <= self.maxArrivalDateFromTheGame)):
                freeTrains.append(train)
        return freeTrains

    def isFoundNewFreeTrains(self):
        self.lock.acquire()

        freeTrains = self.findFreeTrains()
        isFoundNewFreeTrains = (len(freeTrains) > len(self.alreadyFoundFreeTrains))
        if isFoundNewFreeTrains == False:
            for freeTrain in freeTrains:
                isFoundNewFreeTrains = all(freeTrain.id != train.id or freeTrain.freeSeats > train.freeSeats for train in self.alreadyFoundFreeTrains)
        self.alreadyFoundFreeTrains = freeTrains;

        self.lock.release()

        return isFoundNewFreeTrains

