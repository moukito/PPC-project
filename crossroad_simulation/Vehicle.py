from random import sample
from Direction import Direction

TYPES = ["normal, priority"]


class Vehicle:
    def __init__(self, type):
        if type not in TYPES:
            raise TypeError("Wrong type !")
        self.type = type
        self.source, self.destination = sample(Direction.list(), 2)

    def __str__(self):
        return f"type: {self.type}\nsource: {self.source}\ndestination: {self.destination}\n"

    def __repr__(self):
        return {
            "type": {self.type},
            "source": {self.source},
            "destination": {self.destination}
        }