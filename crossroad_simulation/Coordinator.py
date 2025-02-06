import multiprocessing
import os
import random
import signal

import sysv_ipc
from typing import Dict, List
from crossroad_simulation.Vehicle import Vehicle
from crossroad_simulation.Direction import Direction
from crossroad_simulation.Lights import TrafficLights
from crossroad_simulation.LightColor import LightColor
from crossroad_simulation.TimeManager import TimeManager
from crossroad_simulation.Timemanipulator import Timemanipulator


class Coordinator(multiprocessing.Process, Timemanipulator):
	"""
	Manages vehicle movement at the intersection.
	- Uses SysV message queues for inter-process communication.
	- Handles normal traffic based on traffic light rules.
	- Detects priority vehicles and signals the traffic lights immediately.
	"""

	def __init__(self, coordinator_event: multiprocessing.Event, lights_event: multiprocessing.Event, lights_state: dict, light_pid, traffic_queues, traffic_generators, time_manager: TimeManager = TimeManager("auto", 0)) -> None:
		"""Initialize the coordinator with SysV message queues and traffic lights."""
		super().__init__()
		self.traffic_generators = traffic_generators
		self.time_manager = time_manager
		self.coordinator_event = coordinator_event
		self.lights_event = lights_event
		self.lights_state = lights_state
		self.light_pid = light_pid
		self.roads: Dict[Direction, List[Vehicle]] = {direction: [] for direction in Direction}
		self.traffic_queues = traffic_queues

	def run(self):
		"""Main loop that processes traffic from all directions."""
		while True:
			self.accept_traffic()
			self.move_vehicle()
			self.next()

	def next(self, unit=1):
		self.coordinator_event.set()
		self.time_manager.sleep(unit)
		self.lights_event.wait()
		for traffic in self.traffic_generators:
			traffic.wait()
		self.coordinator_event.clear()

	def accept_traffic(self):
		"""Checks for priority vehicles and signals the traffic lights if needed."""
		for direction, queue in self.traffic_queues.items():
			try:
				message, _ = queue.receive(block=False)  # Non-blocking check
				vehicle: Vehicle = message.decode()

				self.roads[direction].append(vehicle)
			except sysv_ipc.ExistentialError:
				print(f"[Coordinator] Error: Message queue for {self.source} does not exist!\n")
			except Exception as e:
				print(f"[Coordinator] Error: {e}\n")

	def move_vehicle(self):
		self.lights_event.wait()

		green_roads = []
		for direction, vehicle_list in self.roads.items():
			if self.lights_state[direction] == LightColor.GREEN.value:
				green_roads.append(direction)
		
		if len(green_roads) == 1:
			direction = green_roads[0]
			if self.roads[direction]:
				print(f"[Coordinator] Moving vehicle from {direction}.")
				if self.roads[direction].pop(0).type == "priority":
					os.kill(self.light_pid, signal.SIGUSR2)

		elif len(green_roads) == 2:
			d1, d2 = green_roads
			results = []

			if self.roads[d1][0].destination != self.roads[d2][0].destination.get_right():
				print(f"Moving vehicle from {d1} to {self.roads[d1][0].destination}.")
				results.append(self.roads[d1].pop)

			if self.roads[d2][0].destination != self.roads[d1][0].destination.get_right():
				print(f"Moving vehicle from {d2} to {self.roads[d2][0].destination}.")
				results.append(self.roads[d2].pop)

			if len(results) == 0:
				r = random.random()
				if r < 0.5:
					print(f"Moving vehicle from {d1} to {self.roads[d1][0].destination}.")
					self.roads[d1].pop(0)
				else:
					print(f"Moving vehicle from {d2} to {self.roads[d2][0].destination}.")
					self.roads[d2].pop(0)

			for result in results:
				result(0)
