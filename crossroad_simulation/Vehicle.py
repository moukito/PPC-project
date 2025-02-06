from crossroad_simulation.Direction import Direction

TYPES = ["normal", "priority"]


class Vehicle:
    """
    Represents a vehicle in the traffic simulation.
    """

    def __init__(self, type: str, source: Direction, destination: Direction):
        """
        Initializes a vehicle with a type, source direction, and destination direction.

        :param type: Type of the vehicle ('normal' or 'priority').
        :param source: Source direction of the vehicle.
        :param destination: Destination direction of the vehicle.
        :raises TypeError: If the vehicle type is not valid.
        :raises ValueError: If the source or destination direction is not valid.
        """
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
        """
        Returns a string representation of the vehicle.

        :return: String representation of the vehicle.
        """
        return f"type: {self.type}\nsource: {self.source}\ndestination: {self.destination}\n"

    @staticmethod
    def str_to_vehicle(string):
        """
        Converts a string representation of a vehicle back to a Vehicle object.

        :param string: String representation of a vehicle.
        :return: Vehicle object.
        """
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
