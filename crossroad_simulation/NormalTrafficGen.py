import multiprocessing
import sysv_ipc
import signal
import os
from crossroad_simulation.Vehicle import Vehicle
from crossroad_simulation.Direction import Direction
from crossroad_simulation.Lights import TrafficLights
from crossroad_simulation.TimeManager import TimeManager
from crossroad_simulation.Timemanipulator import Timemanipulator

MAX_VEHICLES_IN_QUEUE = 5  # Maximum queue size per direction


class NormalTrafficGen(multiprocessing.Process, Timemanipulator):

    def __init__(self, traffic_event, coordinator_event, queue_event: multiprocessing.Event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
        super().__init__()
        self.traffic_event = traffic_event
        self.coordinator_event = coordinator_event
        self.traffic_queues = traffic_queues
        self.queue_event = queue_event  # Unique event per direction
        self.traffic_lights = traffic_lights
        self.time_manager = time_manager

    def run(self):
        try:
            while True:
                print(f"[TrafficGen] Queue Status : {self.source.name}: {self.traffic_queues.current_messages}/{MAX_VEHICLES_IN_QUEUE}\n")

                if self.traffic_queues.current_messages < MAX_VEHICLES_IN_QUEUE:
                    vehicle = Vehicle(self.vehicle_type, self.source, None)
                    message = str(vehicle).encode()
                    self.traffic_queues.send(message)
                    print(f"[TrafficGen] Sent {self.vehicle_type} vehicle from {self.source}\n")

                    # If it's a priority vehicle, notify TrafficLights
                    if self.vehicle_type == "priority":
                        self.send_priority_signal(vehicle)

                    self.queue_event.set()  # Indicate that a new vehicle is added
                else:
                    self.queue_event.clear()  # Queue full, wait before adding more
                    print(f"[TrafficGen] Queue full for {self.source}. Waiting for space...\n")
                    self.queue_event.wait()
                if self.vehicle_type == "priority":
                    self.time_manager.sleep(30)
                else:
                    self.time_manager.sleep(2)
        except sysv_ipc.ExistentialError:
            print(f"[TrafficGen] Error: Message queue for {self.source} does not exist!\n")
        except Exception as e:
            print(f"[TrafficGen] Error: {e}\n")

    def next(self, unit=1):
        self.traffic_event.set()
        self.time_manager.sleep(unit)
        self.coordinator_event.wait()
        self.traffic_event.clear()

    def send_priority_signal(self, vehicle: Vehicle):
        self.traffic_lights.send_signal(vehicle.source)
