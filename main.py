import multiprocessing
import time

from crossroad_simulation import *

if __name__ == "__main__":
	light_event = multiprocessing.Event()
	coordinator_event = multiprocessing.Event()

	lights = TrafficLights(light_event, coordinator_event)
	coordinator = Coordinator(coordinator_event, light_event, lights.get_shared_lights_state(), lights.getpid())

	lights.start()
	coordinator.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		lights.terminate()
		coordinator.terminate()
