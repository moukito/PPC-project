import os
import queue
import time
import signal
import multiprocessing
from multiprocessing import Value
from crossroad_simulation.Direction import Direction
from crossroad_simulation.TimeManager import TimeManager
from crossroad_simulation.LightColor import LightColor
from crossroad_simulation.Timemanipulator import Timemanipulator


class TrafficLights(multiprocessing.Process, Timemanipulator):
	"""
	Manages the traffic lights at the intersection.
	- Normal mode: Opposing lights share the same state (North-South, East-West).
	- Priority mode: Only the light in the direction of the priority vehicle's approach turns green.
	"""

	def __init__(self, lights_event, coordinator_event, time_manager=TimeManager("auto", 0)):
		"""Initialize shared memory for four traffic lights and priority event."""
		super().__init__()
		self.lights_state = {direction: Value('i', LightColor.RED) for direction in Direction}  # Shared light states
		self.priority_direction = multiprocessing.Value('i', -1)  # Stores the index of the priority direction
		self.event = multiprocessing.Event()
		signal.signal(signal.SIGUSR1, self.priority_signal_handler)
		self.queue = queue.Queue()
		self.lights_event = lights_event
		self.coordinator_event = coordinator_event
		self.time_manager = time_manager

	def get_shared_lights_state(self):
		"""
		Provides access to the shared lights_state for external processes.
		Returns the dictionary of shared memory objects representing light states.
		"""
		return self.lights_state

	def run(self):
		"""Main loop to control traffic lights."""
		while True:
			if not self.queue.empty():
				self.handle_priority_vehicle()
				while not self.event.is_set():
					self.next()
				self.event.clear()
			else:
				self.toggle_normal_cycle()
				for i in range(5):
					self.next()

	def next(self, unit: int = 1):
		self.lights_event.set()
		self.time_manager.sleep(unit)
		self.coordinator_event.wait()
		self.lights_event.clear()

	def toggle_normal_cycle(self):
		"""Switches traffic lights in normal mode (North-South green, East-West red, then switch)."""
		current_ns = self.lights_state[Direction.NORTH].value  # Get current North-South light state

		# Toggle states: North-South and East-West must be opposite
		new_ns = LightColor.GREEN if current_ns == LightColor.RED else LightColor.RED
		new_ew = LightColor.RED if new_ns == LightColor.GREEN else LightColor.GREEN

		for direction in [Direction.NORTH, Direction.SOUTH]:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction] = new_ns

		for direction in [Direction.EAST, Direction.WEST]:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction] = new_ew

		print(
			f"[TrafficLights] Normal mode: North-South {'GREEN' if new_ns == LightColor.GREEN else 'RED'}, East-West {'GREEN' if new_ew == LightColor.GREEN else 'RED'}")

	def handle_priority_vehicle(self):
		"""Turns only the priority direction's light green while setting all others to red."""
		priority_dir_index = self.queue.get()
		if priority_dir_index == -1:
			return  # No valid priority direction set

		priority_dir = list(Direction)[priority_dir_index]

		# Set all lights to RED first
		for direction in Direction:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction] = LightColor.RED

		# Set only the priority direction to GREEN
		with self.lights_state[priority_dir].get_lock():
			self.lights_state[priority_dir] = LightColor.GREEN

		print(f"[TrafficLights] Priority vehicle detected! Green light for {priority_dir}, all others set to RED.")

	def priority_signal_handler(self, signum, frame):
		"""Handles SIGUSR1 signal for priority vehicle detection."""
		print("[TrafficLights] Received priority vehicle signal!")
		if signum == signal.SIGUSR1:
			if self.priority_direction.value != -1:
				self.queue.put(self.priority_direction.value)
				self.priority_direction.value = -1
		elif signum == signal.SIGUSR2:
			self.event.set()

	def set_priority_direction(self, direction: str):
		"""Sets the priority direction before sending the signal."""
		if direction in Direction:
			self.priority_direction.value = Direction(direction).value
			print(f"[TrafficLights] Priority vehicle approaching from {direction}")

	@staticmethod
	def getpid():
		return os.getpid()


if __name__ == "__main__":
	lights_event = multiprocessing.Event()
	coordinator_event = multiprocessing.Event()

	traffic_lights = TrafficLights(lights_event, coordinator_event, TimeManager("auto", 2))
	traffic_lights.start()

	try:
		coordinator_event.set()
		with traffic_lights.priority_direction.get_lock(): # todo : factorise it
			traffic_lights.set_priority_direction("North")
			os.kill(traffic_lights.pid, signal.SIGUSR1)
		time.sleep(4)
		os.kill(traffic_lights.pid, signal.SIGUSR2)
		traffic_lights.join()
	except KeyboardInterrupt:
		print("\n[TrafficLights] Stopping simulation.")
		traffic_lights.terminate()
