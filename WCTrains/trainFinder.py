import requests
import json
from datetime import datetime
from trainType import TrainType
from train import Train

class TrainFinder:
	def __init__(self, gameUrl, minDepartureDateToTheGame, maxArrivalDateFromTheGame):
		self.gameUrl = gameUrl
		self.minDepartureDateToTheGame = minDepartureDateToTheGame
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
		

	def findTrains(self):
		response = requests.get(self.gameUrl)
		trainsJson = response.json()
		trains = self.jsonToTrain(trainsJson[0], TrainType.FROM)
		trains.extend(self.jsonToTrain(trainsJson[1], TrainType.TO))
		return trains

	def findFreeTrains(self):
		trains = self.findTrains()
		trains = [train for train in trains if train.freeSeats > 0]
		return trains

