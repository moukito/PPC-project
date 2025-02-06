from crossroad_simulation.Direction import Direction
from random import sample

TYPES = ["normal", "priority"]


class Vehicle:
    def __init__(self, type, source: Direction = None, destination: Direction = None):
        if type not in TYPES:
            raise TypeError("Wrong type !")
        self.type = type

        if source is not None and source not in Direction:
            raise ValueError("Source is not a legal direction !")

        if destination is not None and destination not in Direction:
            raise ValueError("Destination is not a legal direction !")

        directions = Direction.list()

        if source is None and destination is None:
            self.source, self.destination = sample(directions, 2)
        elif source is None:
            self.destination = destination
            self.source = sample([d for d in directions if d != destination], 1)[0]
        elif destination is None:
            self.source = source
            self.destination = sample([d for d in directions if d != source], 1)[0]
        elif source == destination:
            raise ValueError("Source and destination must be different !")
        else:
            self.source = source
            self.destination = destination

    def __str__(self):
        return f"type: {self.type}\nsource: {self.source}\ndestination: {self.destination}\n"


if __name__ == "__main__":
    vehicle = Vehicle("normal", Direction.NORTH, Direction.WEST)
    print(vehicle)
