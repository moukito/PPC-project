import multiprocessing
import random
import sysv_ipc
from crossroad_simulation.Vehicle import Vehicle
from crossroad_simulation.Direction import Direction
from crossroad_simulation.Lights import TrafficLights
from crossroad_simulation.TimeManager import TimeManager
from crossroad_simulation.TimeManipulator import TimeManipulator

MAX_VEHICLES_IN_QUEUE = 5  # Maximum queue size per direction


class NormalTrafficGen(multiprocessing.Process, TimeManipulator):
    """
    Generates normal traffic for the simulation.
    Inherits from multiprocessing.Process to run in a separate process and TimeManipulator for time management.
    """

    def __init__(self, traffic_event: multiprocessing.Event, coordinator_event: multiprocessing.Event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
        """
        Initializes the NormalTrafficGen process.
        
        :param traffic_event: Event to signal traffic generation.
        :param coordinator_event: Event to coordinate with the main process.
        :param traffic_lights: Instance of TrafficLights to manage traffic light states.
        :param traffic_queues: Dictionary of message queues for each direction.
        :param time_manager: Instance of TimeManager to manage simulation time.
        """
        super().__init__()
        self.traffic_event = traffic_event
        self.coordinator_event = coordinator_event
        self.traffic_queues = traffic_queues
        self.traffic_lights = traffic_lights
        self.time_manager = time_manager

    def run(self):
        """
        Main loop of the traffic generator process.
        Continuously generates and sends vehicles if conditions are met.
        """
        while True:
            if self.vehicle_to_send():
                vehicle = self.generate_vehicle()
                self.send_message(vehicle)
            self.next()

    def send_message(self, vehicle):
        """
        Sends a vehicle message to the appropriate queue.
        
        :param vehicle: Vehicle instance to be sent.
        """
        try:
            if self.traffic_queues[vehicle.source].current_messages < MAX_VEHICLES_IN_QUEUE:
                message = str(vehicle).encode()
                self.traffic_queues[vehicle.source].send(message)
                print(f"[TrafficGen] Sent {vehicle.type} vehicle from {vehicle.source}\n")
        except sysv_ipc.ExistentialError:
            pass

    def next(self, unit=1):
        """
        Advances the simulation by a given number of time units.
        
        :param unit: Number of time units to advance.
        """
        self.traffic_event.set()
        self.time_manager.sleep(unit)
        self.coordinator_event.wait()
        self.traffic_event.clear()

    @staticmethod
    def vehicle_to_send():
        """
        Determines whether a vehicle should be sent based on a random probability.
        
        :return: True if a vehicle should be sent, False otherwise.
        """
        return random.random() < 0.6

    @staticmethod
    def generate_vehicle():
        """
        Generates a new vehicle with random source and destination directions.
        
        :return: A new Vehicle instance.
        """
        source, destination = NormalTrafficGen.generate_direction()
        return Vehicle("normal", source, destination)

    @staticmethod
    def generate_direction():
        """
        Randomly generates source and destination directions for a vehicle.
        
        :return: Tuple containing source and destination directions.
        """
        alea = random.random()
        if alea < 0.25:
            source = Direction.EAST
        elif alea < 0.5:
            source = Direction.NORTH
        elif alea < 0.75:
            source = Direction.SOUTH
        else:
            source = Direction.WEST

        source = Direction(source)

        destination = None
        while destination is None:
            alea = random.random()
            if source != Direction.EAST and alea < 0.25:
                destination = Direction.EAST
            elif source != Direction.NORTH and alea < 0.5:
                destination = Direction.NORTH
            elif source != Direction.SOUTH and alea < 0.75:
                destination = Direction.SOUTH
            elif source != Direction.WEST:
                destination = Direction.WEST

        destination = Direction(destination)

        return source, destination
