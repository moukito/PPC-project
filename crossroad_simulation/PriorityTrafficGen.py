from Vehicle import Vehicle
from Lights import TrafficLights
from random import uniform
from json import dumps
from time import sleep
import sysv_ipc
import signal
import os


MESSAGE_QUEUE_KEYS = {"North": 1000, "South": 1001, "East": 1002, "West": 1003}


def priorityTrafficGen(vehicle: Vehicle):
    """
    Generate priority vehicles
    """
    if vehicle.type != "priority":
        raise TypeError("Not a priority vehicle !")
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[vehicle.source], sysv_ipc.IPC_CREAT)
        while True:
            message = dumps(vehicle).encode()

            mq.send(message)

            print(f"[Priority Traffic Generator] Sent priority vehicle on {vehicle.source}\n")
            
            sleep(uniform(1, 5))

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
    vehicle = Vehicle("priority")
    priorityTrafficGen(vehicle)