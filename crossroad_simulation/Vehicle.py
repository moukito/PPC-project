from crossroad_simulation.Direction import Direction
from random import sample

TYPES = ["normal", "priority"]


class Vehicle:
    def __init__(self, type, source: Direction, destination: Direction):
        if type not in TYPES:
            raise TypeError("Wrong type !")
        if source not in Direction:
            raise ValueError("Source is not a legal direction !")
        if destination not in Direction:
            raise ValueError("Destination is not a legal direction !")

        self.type = type
        self.source = source
        self.destination = destination

    def __str__(self):
        return f"type: {self.type}\nsource: {self.source}\ndestination: {self.destination}\n"

    @staticmethod
    def str_to_vehicle(string):
        lines = string.strip().split("\n")
        vehicle_type = lines[0].split(": ")[1]
        source = lines[1].split(": ")[1]
        destination = lines[2].split(": ")[1]

        source = Direction(source)
        destination = Direction(destination)

        return Vehicle(vehicle_type, source, destination)


if __name__ == "__main__":
    vehicle = Vehicle("normal", Direction.NORTH, Direction.WEST)
    print(vehicle)
