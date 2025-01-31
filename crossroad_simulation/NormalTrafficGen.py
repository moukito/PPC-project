import Vehicle
import sysv_ipc
from random import uniform
from json import dumps
from time import sleep

MESSAGE_QUEUE_KEYS = {"north": 1000, "south": 1001, "east": 1002, "west": 1003}

def normalTrafficGen(vehicle: Vehicle):
    if vehicle.type != "normal":
        raise TypeError("Not a normal vehicle !")
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[vehicle.source], sysv_ipc.IPC_CREAT)
        while True:
            message = dumps(vehicle).encode()

            mq.send(message)

            print(f"[Generator] Sent normal vehicle on {vehicle.source}\n")

            sleep(uniform(1, 5))

    except Exception as e:
        print(f"[Generator] Error: {e}")

if __name__ == "__main__":
    vehicle = Vehicle("normal")
    normalTrafficGen()