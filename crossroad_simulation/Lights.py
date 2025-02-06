import os
import queue
import signal
import multiprocessing
from crossroad_simulation.Direction import Direction
from crossroad_simulation.TimeManager import TimeManager
from crossroad_simulation.LightColor import LightColor
from crossroad_simulation.TimeManipulator import TimeManipulator


class TrafficLights(multiprocessing.Process, TimeManipulator):
	"""
	Manages the traffic lights at the intersection.
	- Normal mode: Opposing lights share the same state (North-South, East-West).
	- Priority mode: Only the light in the direction of the priority vehicle's approach turns green.
	"""

	def __init__(self, shared_lights, lights_event, coordinator_event, time_manager=TimeManager("auto", 0)):
		"""
		Initialize shared memory for four traffic lights and priority event.

		:param shared_lights: Shared dictionary representing the state of the traffic lights.
		:param lights_event: Event to signal traffic light changes.
		:param coordinator_event: Event to coordinate with the main process.
		:param time_manager: Instance of TimeManager to manage simulation time.
		"""
		super().__init__()
		self.lights_state = shared_lights
		self.lock = multiprocessing.Lock()
		self.priority_direction = "default"
		self.event = multiprocessing.Event()
		signal.signal(signal.SIGUSR1, self.priority_signal_handler)
		signal.signal(signal.SIGUSR2, self.priority_signal_handler)
		self.queue = multiprocessing.Queue()
		self.lights_event = lights_event
		self.coordinator_event = coordinator_event
		self.time_manager = time_manager

	def get_shared_lights_state(self):
		"""
		Provides access to the shared lights_state for external processes.

		:return: Dictionary of shared memory objects representing light states.
		"""
		return self.lights_state

	def run(self):
		"""
		Main loop to control traffic lights.
		"""
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
		"""
		Advances the simulation by a given number of time units.

		:param unit: Number of time units to advance.
		"""
		self.lights_event.set()
		self.time_manager.sleep(unit)
		self.coordinator_event.wait()
		self.lights_event.clear()

	def toggle_normal_cycle(self):
		"""
		Switches traffic lights in normal mode (North-South green, East-West red, then switch).
		"""
		current_ns = self.lights_state[Direction.NORTH]

		new_ns = LightColor.GREEN.value if current_ns == LightColor.RED.value else LightColor.RED.value
		new_ew = LightColor.RED.value if new_ns == LightColor.GREEN.value else LightColor.GREEN.value

		for direction in [Direction.NORTH, Direction.SOUTH]:
			with self.lock:
				self.lights_state[direction] = new_ns

		for direction in [Direction.EAST, Direction.WEST]:
			with self.lock:
				self.lights_state[direction] = new_ew

	def handle_priority_vehicle(self):
		"""
		Turns only the priority direction's light green while setting all others to red.
		"""
		priority_dir = Direction(self.queue.get())
		if priority_dir == "default":
			return

		for direction in Direction:
			with self.lock:
				self.lights_state[direction] = LightColor.RED.value

		with self.lock:
			self.lights_state[priority_dir] = LightColor.GREEN.value

	def priority_signal_handler(self, signum, frame):
		"""
		Handles SIGUSR1 signal for priority vehicle detection.

		:param signum: Signal number.
		:param frame: Current stack frame.
		"""
		if signum == signal.SIGUSR1:
			if self.priority_direction != "default":
				self.queue.put(self.priority_direction)
				self.priority_direction = "default"
		elif signum == signal.SIGUSR2:
			self.event.set()

	def set_priority_direction(self, direction: Direction):
		"""
		Sets the priority direction before sending the signal.

		:param direction: Direction of the priority vehicle.
		"""
		self.priority_direction = direction.value

	@staticmethod
	def getpid():
		"""
		Returns the process ID of the current process.

		:return: Process ID.
		"""
		return os.getpid()

	def send_signal(self, direction: Direction):
		"""
		Sends a signal to the traffic lights process to handle a priority vehicle.

		:param direction: Direction of the priority vehicle.
		"""
		with self.lock:
			self.set_priority_direction(direction)
			os.kill(self.getpid(), signal.SIGUSR1)
