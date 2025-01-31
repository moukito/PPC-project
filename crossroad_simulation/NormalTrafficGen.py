from Vehicle import Vehicle
import sysv_ipc
from random import uniform
from json import dumps
from time import sleep
from Direction import Direction

MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}


def normalTrafficGen(vehicle: Vehicle):
    """
    Genarate normal vehicles
    """
    if vehicle.type != "normal":
        raise TypeError("Not a normal vehicle !")
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[Direction(vehicle.source)], sysv_ipc.IPC_CREAT)
        while True:
            message = dumps(vehicle.to_dict()).encode()

            mq.send(message)

            print(f"[Normal Traffic Generator] Sent normal vehicle on {vehicle.source}\n")

            sleep(uniform(1, 5))

    except Exception as e:
        print(f"[Normal Traffic Generator] Error: {e}")


if __name__ == "__main__":
    vehicle = Vehicle("normal")
    normalTrafficGen(vehicle)