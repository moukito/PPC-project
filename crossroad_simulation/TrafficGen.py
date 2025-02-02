from Vehicle import Vehicle
from random import uniform
from time import sleep
from Direction import Direction
from Lights import TrafficLights
import sysv_ipc
import threading
import signal
import os


MESSAGE_QUEUE_KEYS = {direction: 1000 + i for i, direction in enumerate(Direction)}
MAX_VEHICLES_IN_QUEUE = 10
queue_free = threading.Event()  # Indicate when the queue has available space
lock = threading.Lock() # Single global lock for synchronization


def normal_traffic_gen(source: Direction):
    """ 
    Generates normal vehicles with synchronization and congestion handling
    """
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)

        while True:
            with lock:  # Lock access to the message queue
                print(f"[Queue Status] {source.name}: {mq.current_messages}/{MAX_VEHICLES_IN_QUEUE}")

                if mq.current_messages < MAX_VEHICLES_IN_QUEUE:
                    vehicle = Vehicle("normal", source, None)
                    message = str(vehicle).encode()
                    mq.send(message)
                    print(f"[Normal Traffic Generator] Sent normal vehicle on {source.name}\n")
                    queue_free.set()  # Indicate the queue has space
                else:
                    queue_free.clear()  # Indicate the queue is full
                    print(f"[Normal Traffic Generator] Path for {source.name} is congested! Blocking new vehicles...\n")

                    queue_free.wait()  # Wait until the queue has space
            sleep(uniform(1, 3))  # Pause before adding another vehicle

    except sysv_ipc.ExistentialError:
        print(f"[Normal Traffic Generator] Error: Message queue for {source.name} already exists!")
    except Exception as e:
        print(f"[Normal Traffic Generator] Error: {e}")

def priority_traffic_gen(source: Direction):
    """ 
    Generates priority vehicles with synchronization and congestion handling
    """
    try:
        mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)

        while True:
            with lock:  # Lock access to the message queue
                print(f"[Queue Status] {source.name}: {mq.current_messages}/{MAX_VEHICLES_IN_QUEUE}")

                if mq.current_messages < MAX_VEHICLES_IN_QUEUE:
                    vehicle = Vehicle("priority", source, None)
                    message = str(vehicle).encode()
                    mq.send(message)
                    print(f"[Priority Traffic Generator] Sent priority vehicle on {source.name}\n")
                    queue_free.set()  # Indicate the queue has space
                else:
                    queue_free.clear()  # Indicate the queue is full
                    print(f"[Priority Traffic Generator] Path for {source.name} is congested! Blocking new vehicles...\n")
                    queue_free.wait()  # Wait until the queue has space
            sleep(uniform(1, 3))  # Pause before adding another vehicle

    except sysv_ipc.ExistentialError:
        print(f"[Priority Traffic Generator] Error: Message queue for {source.name} already exists!")
    except Exception as e:
        print(f"[Priority Traffic Generator] Error: {e}")


def send_priority_signal(traffic_lights: TrafficLights, vehicle: Vehicle):
    """
    Send a priority signal SIGUSR1 to the TrafficLights process for an approaching emergency and safely updating the priority direction
    """
    with traffic_lights.priority_direction.get_lock():
        traffic_lights.set_priority_direction(vehicle.source)
        print(f"[Priority Traffic Generator] Priority vehicle detected from {vehicle.source}, sending SIGUSR1...")
        os.kill(traffic_lights.pid, signal.SIGUSR1)


def clear_a_vehicle(source: Direction):
    """
    Removes one vehicle from the message queue for the given source direction.
    """
    mq = sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT)

    if mq.current_messages > 0:
        message, _ = mq.receive()
        print(f"[Clear Vehicle] Removed: {message.decode()} from {source.name}")
        queue_free.set()


def clear_all_vehicles():
    """
    Clear all vehicles from all directions but not remove any message queue 
    """
    for mq in [sysv_ipc.MessageQueue(MESSAGE_QUEUE_KEYS[source], sysv_ipc.IPC_CREAT) for source in Direction]:
        while mq.current_messages > 0:
            mq.receive()
        queue_free.set
    print(f"\n[Clear Vehicles] All vehicles are removed !\n")


if __name__ == "__main__":
    clear_all_vehicles()

    source = Direction.NORTH

    normal_thread = threading.Thread(target=normal_traffic_gen, args=(source,))
    priority_thread = threading.Thread(target=priority_traffic_gen, args=(source,))

    normal_thread.start()
    priority_thread.start()

    sleep(15)
    clear_a_vehicle(Direction.NORTH)

    normal_thread.join()
    priority_thread.join()