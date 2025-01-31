import Vehicle
import sysv_ipc
import signal
from random import uniform
from json import dumps
from time import sleep

MESSAGE_QUEUE_KEYS = {"north": 1000, "south": 1001, "east": 1002, "west": 1003}

def normalTrafficGen(vehicle: Vehicle):
    if vehicle.type != "priority":
        raise TypeError("Not a priority vehicle !")
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[vehicle.source], sysv_ipc.IPC_CREAT)
        while True:
            message = dumps(vehicle).encode()

            mq.send(message)

            print(f"[Generator] Sent priority vehicle on {vehicle.source}\n")
            
            sleep(uniform(1, 5))

    except Exception as e:
        print(f"[Generator] Error: {e}")

def handler

if __name__ == "__main__":
    vehicle = Vehicle("priority")
    signal.signal(signal.SIGUSR1, handler)
    normalTrafficGen()