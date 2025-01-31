import multiprocessing
import sysv_ipc
from Vehicle import Vehicle
from Direction import Direction
from Lights import TrafficLights
from crossroad_simulation.TimeManager import TimeManager


class Coordinator(multiprocessing.Process):
	"""
	Manages vehicle movement at the intersection.
	- Uses SysV message queues for inter-process communication.
	- Handles normal traffic based on traffic light rules.
	- Detects priority vehicles and signals the traffic lights immediately.
	"""

	def __init__(self, coordinator_event: multiprocessing.Event, lights_event: multiprocessing.Event, lights_state: dict, time_manager: TimeManager = TimeManager("auto", 0)) -> None:
		"""Initialize the coordinator with SysV message queues and traffic lights."""
		super().__init__()
		self.time_manager = time_manager
		self.coordinator_event = coordinator_event
		self.lights_event = lights_event
		self.lights_state = lights_state
		self.roads = {direction: [] for direction in Direction}
		self.traffic_queues = {direction: sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		                       for key, direction in zip(range(1000, 1004), Direction)}  # Unique keys for queues

	def process_traffic(self):
		"""Main loop that processes traffic from all directions."""
		while True:
			self.accept_traffic()
			self.move_vehicle()
			self.next()

	def next(self, unit=1):  # todo : abstract this method
		self.coordinator_event.set()
		self.time_manager.sleep(unit)
		self.lights_event.wait()
		self.coordinator_event.clear()

	def accept_traffic(self):
		"""Checks for priority vehicles and signals the traffic lights if needed."""
		for direction, queue in self.traffic_queues.items():
			try:
				message, _ = queue.receive(block=False)  # Non-blocking check
				vehicle: Vehicle = message.decode()

				self.roads[direction].append(vehicle)
			except sysv_ipc.ExistentialError:  # todo check this
				pass  # Queue not found (should not happen)
			except sysv_ipc.BusyError:
				pass  # No messages in queue

	def move_vehicle(self):
		self.lights_event.wait()
		green_roads = []
		for direction, vehicle_list in self.roads.items():
			if self.lights_state[direction].value == 0:  # todo : green value
				green_roads.append(direction)
		
		if len(green_roads) == 1:
			direction = green_roads[0]
			if self.roads[direction]:
				print(f"[Coordinator] Moving vehicle from {direction}.")
				self.roads[direction].pop(0)
		elif len(green_roads) == 2:
			d1, d2 = green_roads  # todo : a check
			if self.roads[d1] and self.roads[d1][0].destination == d2:
				print(f"Moving vehicle from {d1} to {d2}.")
				self.roads[d1].pop(0)  # Move the first vehicle on d1
			elif self.roads[d2] and self.roads[d2][0].destination == d1:
				print(f"Moving vehicle from {d2} to {d1}.")
				self.roads[d2].pop(0)  # Move the first vehicle on d2


if __name__ == "__main__":
	traffic_lights = TrafficLights()
	coordinator = Coordinator()
	coordinator.start()

	try:
		coordinator.join()
	except KeyboardInterrupt:
		print("\n[Coordinator] Stopping simulation.")
		coordinator.terminate()
