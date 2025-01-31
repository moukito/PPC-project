import multiprocessing
import os
import sysv_ipc
import time
import signal
from Lights import TrafficLights, DIRECTIONS
from crossroad_simulation.TimeManager import TimeManager


class Coordinator(multiprocessing.Process):
	"""
	Manages vehicle movement at the intersection.
	- Uses SysV message queues for inter-process communication.
	- Handles normal traffic based on traffic light rules.
	- Detects priority vehicles and signals the traffic lights immediately.
	"""

	def __init__(self, coordinator_event, lights_event, time_manager=TimeManager("auto", 0)):
		"""Initialize the coordinator with SysV message queues and traffic lights."""
		super().__init__()
		self.time_manager = time_manager
		self.coordinator_event = coordinator_event
		self.lights_event = lights_event
		self.traffic_queues = {direction: sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
		                       for key, direction in zip(range(1000, 1004), DIRECTIONS)}  # Unique keys for queues

	def process_traffic(self):
		"""Main loop that processes traffic from all directions."""
		while True:
			self.manage_traffic()
			self.next(1)

	def next(self, unit):  # todo : abstract this method
		self.coordinator_event.set()
		self.time_manager.sleep(unit)
		self.lights_event.wait()
		self.coordinator_event.clear()

	def manage_traffic(self):
		"""Checks for priority vehicles and signals the traffic lights if needed."""
		for direction, queue in self.traffic_queues.items():
			try:
				message, _ = queue.receive(block=False)  # Non-blocking check
				vehicle = message.decode()

				if "priority" in vehicle:
					print(f"[Coordinator] Priority vehicle detected from {direction}.")
			except sysv_ipc.ExistentialError:
				pass  # Queue not found (should not happen)
			except sysv_ipc.BusyError:
				pass  # No messages in queue


if __name__ == "__main__":
	traffic_lights = TrafficLights()
	coordinator = Coordinator()
	coordinator.start()

	try:
		coordinator.join()
	except KeyboardInterrupt:
		print("\n[Coordinator] Stopping simulation.")
		coordinator.terminate()
