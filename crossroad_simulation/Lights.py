import os
import time
import signal
import multiprocessing
from multiprocessing import Value

# Traffic light states
RED = 0
GREEN = 1

# Directions at the intersection
DIRECTIONS = ["North", "South", "East", "West"]


class TrafficLights(multiprocessing.Process):
	"""
	Manages the traffic lights at the intersection.
	- Normal mode: Opposing lights share the same state (North-South, East-West).
	- Priority mode: Only the light in the direction of the priority vehicle's approach turns green.
	"""

	def __init__(self):
		"""Initialize shared memory for four traffic lights and priority event."""
		super().__init__()
		self.lights_state = {direction: Value('i', RED) for direction in DIRECTIONS}  # Shared light states
		self.priority_event = multiprocessing.Event()  # Event for priority vehicle detection
		self.priority_direction = multiprocessing.Value('i', -1)  # Stores the index of the priority direction
		signal.signal(signal.SIGUSR1, self.priority_signal_handler)

	def run(self):
		"""Main loop to control traffic lights."""
		while True:
			if self.priority_event.is_set():
				self.handle_priority_vehicle()
				self.priority_event.clear()
			else:
				self.toggle_normal_cycle()
				time.sleep(10)

	def toggle_normal_cycle(self):
		"""Switches traffic lights in normal mode (North-South green, East-West red, then switch)."""
		current_ns = self.lights_state["North"].value  # Get current North-South light state

		# Toggle states: North-South and East-West must be opposite
		new_ns = GREEN if current_ns == RED else RED
		new_ew = RED if new_ns == GREEN else GREEN

		for direction in ["North", "South"]:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction].value = new_ns

		for direction in ["East", "West"]:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction].value = new_ew

		print(
			f"[TrafficLights] Normal mode: North-South {'GREEN' if new_ns == GREEN else 'RED'}, East-West {'GREEN' if new_ew == GREEN else 'RED'}")

	def handle_priority_vehicle(self):
		"""Turns only the priority direction's light green while setting all others to red."""
		priority_dir_index = self.priority_direction.value
		if priority_dir_index == -1:
			return  # No valid priority direction set

		priority_dir = DIRECTIONS[priority_dir_index]

		# Set all lights to RED first
		for direction in DIRECTIONS:
			with self.lights_state[direction].get_lock():
				self.lights_state[direction].value = RED

		# Set only the priority direction to GREEN
		with self.lights_state[priority_dir].get_lock():
			self.lights_state[priority_dir].value = GREEN

		print(f"[TrafficLights] Priority vehicle detected! Green light for {priority_dir}, all others set to RED.")
		time.sleep(5)  # Allow the emergency vehicle to pass

	def priority_signal_handler(self, signum, frame):
		"""Handles SIGUSR1 signal for priority vehicle detection."""
		print("[TrafficLights] Received priority vehicle signal!")
		if self.priority_direction.value != -1:
			self.priority_event.set()

	def set_priority_direction(self, direction: str):
		"""Sets the priority direction before sending the signal."""
		if direction in DIRECTIONS:
			self.priority_direction.value = DIRECTIONS.index(direction)
			print(f"[TrafficLights] Priority vehicle approaching from {direction}")


if __name__ == "__main__":
	traffic_lights = TrafficLights()
	traffic_lights.start()

	try:
		time.sleep(15)
		traffic_lights.set_priority_direction("North")
		os.kill(traffic_lights.pid, signal.SIGUSR1)
		traffic_lights.join()
	except KeyboardInterrupt:
		print("\n[TrafficLights] Stopping simulation.")
		traffic_lights.terminate()
