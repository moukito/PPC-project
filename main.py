import multiprocessing
import time
import sysv_ipc

from crossroad_simulation import *
from crossroad_simulation.TimeManager import TimeManager

if __name__ == "__main__":
	time_manager = TimeManager("auto", 1)

	light_event = multiprocessing.Event()
	coordinator_event = multiprocessing.Event()
	traffic_generators_event = {traffic: multiprocessing.Event() for traffic in ["normal_traffic_generators", "priority_traffic_generators"]}

	queue_events = {direction: multiprocessing.Event() for direction in Direction}
	traffic_queues = {direction: sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT) for key, direction in zip(range(1000, 1004), Direction)}

	lights = TrafficLights(light_event, coordinator_event, time_manager)

	normal_generators = {
		direction: TrafficGen(direction, "normal", queue_events[direction], lights)
		for direction in Direction
	}

	priority_generators = {
		direction: TrafficGen(direction, "priority", queue_events[direction], lights)
		for direction in Direction
	}

	coordinator = Coordinator(coordinator_event, light_event, lights.get_shared_lights_state(), lights.getpid(), traffic_queues, traffic_generators_event.values(), time_manager)

	lights.start()

	for gen in normal_generators.values():
		gen.start()

	for gen in priority_generators.values():
		gen.start()

	coordinator.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		lights.terminate()
		coordinator.terminate()
