from .stadiumType import StadiumType

class Stadium:
    def __init__(self, stadiumType: StadiumType, stadiumName):
        self.stadiumType = stadiumType
        self.stadiumName = stadiumName