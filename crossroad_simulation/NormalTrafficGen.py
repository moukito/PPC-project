from Vehicle import Vehicle
from random import uniform
from time import sleep
from Direction import Direction
import sysv_ipc


MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}


def normalTrafficGen(source: Direction):
    """
    Genarate normal vehicles in the source direction
    """
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)
        vehicle = Vehicle("normal", source, None)

        while True:
            message = str(vehicle).encode()

            mq.send(message)

            print(f"[Normal Traffic Generator] Sent normal vehicle on {source.name}\n")

            sleep(uniform(1, 5))
    
    except sysv_ipc.ExistentialError:
        print(f"[Normal Traffic Generator] Error: Message queue for {source.name} already exists!")

    except Exception as e:
        print(f"[Normal Traffic Generator] Error: {e}")


if __name__ == "__main__":
    print(MESSAGE_QUEUE_KEYS[Direction.NORTH])
    print(Direction.NORTH.name)
    print(Direction.NORTH)
    normalTrafficGen(Direction.NORTH)