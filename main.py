import multiprocessing
import time

from crossroad_simulation import *

if __name__ == "__main__":
	light_event = multiprocessing.Event()
	coordinator_event = multiprocessing.Event()
	queue_events = {direction: multiprocessing.Event() for direction in Direction}

	lights = TrafficLights(light_event, coordinator_event)

	normal_generators = {
		direction: TrafficGen(direction, "normal", queue_events[direction], lights)
		for direction in Direction
	}

	priority_generators = {
		direction: TrafficGen(direction, "priority", queue_events[direction], lights)
		for direction in Direction
	}

	coordinator = Coordinator(coordinator_event, light_event, lights.get_shared_lights_state(), lights.getpid())

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
