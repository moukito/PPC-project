import multiprocessing
import random
from crossroad_simulation import TrafficLights, Vehicle, NormalTrafficGen
from crossroad_simulation.TimeManager import TimeManager


class PriorityTrafficGen(NormalTrafficGen):
	def __init__(self, traffic_event, coordinator_event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
		NormalTrafficGen.__init__(self, traffic_event, coordinator_event, traffic_lights, traffic_queues, time_manager)

	@staticmethod
	def vehicle_to_send():
		return random.random() < 0.3

	def send_priority_signal(self, vehicle: Vehicle):
		self.traffic_lights.send_signal(vehicle.source)

	@staticmethod
	def send_signal(func):
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
		NormalTrafficGen.send_message(self, vehicle)

	@staticmethod
	def generate_vehicle():
		vehicle = NormalTrafficGen.generate_vehicle()
		vehicle.type = "priority"

		return vehicle
