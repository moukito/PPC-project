import multiprocessing
import time
import sysv_ipc

from crossroad_simulation import *
from crossroad_simulation.TimeManager import TimeManager

if __name__ == "__main__":

	with multiprocessing.Manager() as manager:
		shared_lights = manager.dict({direction: LightColor.RED.value for direction in Direction})

		time_manager = TimeManager("auto", 1)

		light_event = multiprocessing.Event()
		coordinator_event = multiprocessing.Event()
		traffic_generators_event = {traffic: multiprocessing.Event() for traffic in ["normal_traffic_generators", "priority_traffic_generators"]}

		traffic_queues = {direction: sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT) for key, direction in zip(range(1000, 1004), Direction)}

		lights = TrafficLights(shared_lights, light_event, coordinator_event, time_manager)

		normal_traffic_generator = NormalTrafficGen(traffic_generators_event["normal_traffic_generators"], coordinator_event, lights, traffic_queues, time_manager)

		priority_traffic_generator = PriorityTrafficGen(traffic_generators_event["priority_traffic_generators"], coordinator_event, lights, traffic_queues, time_manager)

		coordinator = Coordinator(coordinator_event, light_event, lights.get_shared_lights_state(), lights.getpid(), traffic_queues, traffic_generators_event.values(), time_manager)

		display = multiprocessing.Process(target=Display.run_display, args=(coordinator, ))

		lights.start()
		normal_traffic_generator.start()
		priority_traffic_generator.start()
		coordinator.start()
		display.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			lights.terminate()
			normal_traffic_generator.terminate()
			priority_traffic_generator.terminate()
			coordinator.terminate()
			display.terminate()
