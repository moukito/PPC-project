from Vehicle import Vehicle
from random import uniform
from time import sleep
from Direction import Direction
from Lights import TrafficLights
import sysv_ipc
import signal
import os


MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}


def priorityTrafficGen(source: Direction):
    """
    Generate priority vehicles in the source direction
    """
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[Direction(source)], sysv_ipc.IPC_CREAT)
        vehicle = Vehicle("priority", source, None)

        while True:
            message = str(vehicle).encode()

            mq.send(message)

            print(f"[Priority Traffic Generator] Sent priority vehicle on {source.name}\n")
            
            sleep(uniform(60, 120))

    except sysv_ipc.ExistentialError:
        print(f"[Priority Traffic Generator] Error: Message queue for {source.name} already exists!")

    except Exception as e:
        print(f"[Priority Traffic Generator] Error: {e}")


def send_priority_signal(traffic_lights: TrafficLights, vehicle: Vehicle):
    """
    Send a priority signal SIGUSR1 to the TRafficLights process for an approaching emergency and safely updating the priority direction
    """
    with traffic_lights.priority_direction.get_lock():
        traffic_lights.set_priority_direction(vehicle.source)
        print(f"[Priority Traffic Generator] Priority vehicle detected from {vehicle.source}, sending SIGUSR1...")
        os.kill(traffic_lights.pid, signal.SIGUSR1)


if __name__ == "__main__":
    priorityTrafficGen(Direction.NORTH)