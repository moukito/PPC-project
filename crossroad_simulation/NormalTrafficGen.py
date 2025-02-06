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

    def __init__(self, traffic_event: multiprocessing.Event, coordinator_event: multiprocessing.Event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
        super().__init__()
        self.traffic_event = traffic_event
        self.coordinator_event = coordinator_event
        self.traffic_queues = traffic_queues
        self.traffic_lights = traffic_lights
        self.time_manager = time_manager

    def run(self):
        while True:
            if self.vehicle_to_send():
                vehicle = self.generate_vehicle()
                self.send_message(vehicle)
            self.next()

    def send_message(self, vehicle):
        try:
            print(f"[TrafficGen] Queue Status : {vehicle.source.name}: {self.traffic_queues[vehicle.source].current_messages}/{MAX_VEHICLES_IN_QUEUE}\n")
            if self.traffic_queues[vehicle.source].current_messages < MAX_VEHICLES_IN_QUEUE:
                message = str(vehicle).encode()
                self.traffic_queues[vehicle.source].send(message)
                print(f"[TrafficGen] Sent {vehicle.type} vehicle from {vehicle.source}\n")
            else:
                print(f"[TrafficGen] Queue full for {vehicle.source}. Waiting for space...\n")
        except sysv_ipc.ExistentialError:
            print(f"[TrafficGen] Error: Message queue for {vehicle.source} does not exist!\n")
        except Exception as e:
            print(f"[TrafficGen] Error: {e}\n")

    def next(self, unit=1):
        self.traffic_event.set()
        self.time_manager.sleep(unit)
        self.coordinator_event.wait()
        self.traffic_event.clear()

    @staticmethod
    def vehicle_to_send():
        return random.random() < 0.6

    @staticmethod
    def generate_vehicle():
        source, destination = NormalTrafficGen.generate_direction()

        return Vehicle("normal", source, destination)

    @staticmethod
    def generate_direction():
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


if __name__ == '__main__':
    pass


# if __name__ == "__main__":
#     traffic_lights = TrafficLights(lights_event=multiprocessing.Event(), coordinator_event=multiprocessing.Event(), time_manager=TimeManager("auto", 1))
#
#     gen = NormalTrafficGen(traffic_event=multiprocessing.Event(), coordinator_event=multiprocessing.Event(), traffic_lights=traffic_lights, traffic_queues={traffic: multiprocessing.Event() for traffic in ["normal_traffic_generators", "priority_traffic_generators"]}, time_manager=TimeManager("auto", 1))
#     gen.start()
#
#     try:
#         while True:
#             pass
#     except KeyboardInterrupt:
#         gen.terminate()
