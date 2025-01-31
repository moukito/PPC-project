import Vehicle
import sysv_ipc
import signal
from random import uniform
from json import dumps
from time import sleep
from Direction import Direction

MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}


def normalTrafficGen(vehicle: Vehicle):
    if vehicle.type != "priority":
        raise TypeError("Not a priority vehicle !")
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[Direction(vehicle.source)], sysv_ipc.IPC_CREAT)
        while True:
            message = dumps(vehicle).encode()

            mq.send(message)

            print(f"[Generator] Sent priority vehicle on {vehicle.source}\n")
            
            sleep(uniform(1, 5))

    except Exception as e:
        print(f"[Generator] Error: {e}")


if __name__ == "__main__":
    vehicle = Vehicle("priority")
    normalTrafficGen()