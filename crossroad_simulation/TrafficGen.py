import multiprocessing
import sysv_ipc
import signal
import os
from random import uniform, choices
from time import sleep
from Vehicle import Vehicle
from Direction import Direction
from Lights import TrafficLights
from TimeManager import TimeManager

# Define System V message queue keys
MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}
MAX_VEHICLES_IN_QUEUE = 5  # Maximum queue size per direction

class TrafficGen(multiprocessing.Process):
    """
    Traffic Generator Process:
    - Continuously generates vehicles and sends them to Coordinator's message queues.
    - Handles both normal and priority vehicles.
    - Uses an event to prevent queue congestion.
    """
    def __init__(self, source: Direction, queue_event: multiprocessing.Event, lock: multiprocessing.Lock, traffic_lights: TrafficLights, time_manager = TimeManager("auto", 1)):
        super().__init__()
        self.source = source
        self.queue_event = queue_event  # Unique event per direction
        self.lock = lock # Unique lock for message queue !
        self.traffic_lights = traffic_lights

    def run(self):
        """
        The process function that generates and sends vehicles to the message queue.
        Runs continuously with a random time interval.
        """
        try:
            mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[self.source], sysv_ipc.IPC_CREAT)

            while True:
                with self.lock:
                    print(f"[Queue Status] {self.source.name}: {mq.current_messages}/{MAX_VEHICLES_IN_QUEUE}\n")

                    if mq.current_messages < MAX_VEHICLES_IN_QUEUE:
                        vehicle_type = choices(["normal", "priority"], weights = [9, 1])[0]  # Randomly select vehicle type
                        vehicle = Vehicle(vehicle_type, self.source, None)
                        message = str(vehicle).encode()
                        mq.send(message)
                        print(f"[TrafficGen] Sent {vehicle_type} vehicle from {self.source}\n")

                        # If it's a priority vehicle, notify TrafficLights
                        if vehicle_type == "priority":
                            self.send_priority_signal(vehicle)

                        self.queue_event.set()  # Indicate that a new vehicle is added
                    else:
                        self.queue_event.clear()  # Queue full, wait before adding more
                        print(f"[TrafficGen] Queue full for {self.source}. Waiting for space...\n")
                        self.queue_event.wait()
                sleep(uniform(1, 3))  # Randomized vehicle arrival time

        except sysv_ipc.ExistentialError:
            print(f"[TrafficGen] Error: Message queue for {self.source} does not exist!\n")
        except Exception as e:
            print(f"[TrafficGen] Error: {e}\n")

    def send_priority_signal(self, vehicle: Vehicle):
        """
        Sends a priority signal (SIGUSR1) to TrafficLights for an approaching emergency.
        """
        with self.traffic_lights.priority_direction.get_lock():
            self.traffic_lights.set_priority_direction(vehicle.source)
            print(f"[Priority Vehicle] Priority vehicle from {vehicle.source}, sending SIGUSR1...")
            os.kill(self.traffic_lights.pid, signal.SIGUSR1)


def remove_vehicle_from_source(source: Direction, queue_event: multiprocessing.Event):
    """
    Removes one vehicle from the message queue for the given source direction.
    """
    mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)

    if mq.current_messages > 0:
        message, _ = mq.receive()
        print(f"[Clear Vehicle] Removed: {message.decode()} from {source.name}")
        queue_event.set()  # Allow new vehicles to enter queue


def remove_all_vehicles(queue_events: dict):
    """
    Removes all vehicles from all queues but does not delete the queues.
    """
    for source, event in queue_events.items():
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)
        while mq.current_messages > 0:
            mq.receive()
        event.set()  # Allow new vehicles in this direction

    print(f"\n[Clear Vehicles] All vehicles removed!\n")


if __name__ == "__main__":
    # Create separate queue events for each direction
    queue_events = {direction: multiprocessing.Event() for direction in Direction}
    locks = {direction: multiprocessing.Lock() for direction in Direction}
    remove_all_vehicles(queue_events)
    
    lights_event = multiprocessing.Event()
    coordinator_event = multiprocessing.Event()

    # Start TrafficLights process
    traffic_lights = TrafficLights(lights_event, coordinator_event)
    traffic_lights.start()

    # Start vehicle generators for different directions with separate queue events
    generators = {
        direction: TrafficGen(direction, queue_events[direction], locks[direction], traffic_lights)
        for direction in Direction
    }

    # Start all generators
    for gen in generators.values():
        gen.start()

    sleep(10)

    # Ensure all processes exit cleanly
    for gen in generators.values():
        gen.join()
    traffic_lights.join()
