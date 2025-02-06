import multiprocessing
import random
from crossroad_simulation import TrafficLights, Vehicle, NormalTrafficGen
from crossroad_simulation.TimeManager import TimeManager


class PriorityTrafficGen(NormalTrafficGen):
	"""
	Class for generating priority traffic in the simulation.
	Inherits from NormalTrafficGen.
	"""

	def __init__(self, traffic_event, coordinator_event: multiprocessing.Event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
		"""
		Initialize the PriorityTrafficGen.

		:param traffic_event: Event to control traffic generation.
		:param coordinator_event: Event to coordinate with other components.
		:param traffic_lights: Instance of TrafficLights to control traffic lights.
		:param traffic_queues: Queues for managing traffic messages.
		:param time_manager: Instance of TimeManager to manage simulation time.
		"""
		NormalTrafficGen.__init__(self, traffic_event, coordinator_event, traffic_lights, traffic_queues, time_manager)

	@staticmethod
	def vehicle_to_send():
		"""
		Determine if a priority vehicle should be sent.

		:return: True if a priority vehicle should be sent, False otherwise.
		"""
		return random.random() < 0.3

	def send_priority_signal(self, vehicle: Vehicle):
		"""
		Send a priority signal for the given vehicle.

		:param vehicle: The vehicle to send the priority signal for.
		"""
		self.traffic_lights.send_signal(vehicle.source)

	@staticmethod
	def send_signal(func):
		"""
		Decorator to send a priority signal when a vehicle is sent.

		:param func: The function to wrap.
		:return: The wrapped function.
		"""
		def wrapper(self, *args, **kwargs):
			result = func(self, *args, **kwargs)
			for arg in args:
				if type(arg) is Vehicle.Vehicle:
					self.send_priority_signal(arg)
			print("[Priority Traffic Generated]")
			return result

		return wrapper

	@send_signal
	def send_message(self, vehicle: Vehicle):
		"""
		Send a message for the given vehicle.

		:param vehicle: The vehicle to send the message for.
		"""
		NormalTrafficGen.send_message(self, vehicle)

	@staticmethod
	def generate_vehicle():
		"""
		Generate a priority vehicle.

		:return: The generated priority vehicle.
		"""
		vehicle = NormalTrafficGen.generate_vehicle()
		vehicle.type = "priority"
		return vehicle
