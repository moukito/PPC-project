from abc import ABC, abstractmethod


class Timemanipulator(ABC):
	"""
	Abstract base class for traffic-related entities like Coordinator
	and TrafficLights.
	"""

	@abstractmethod
	def next(self, unit: int = 1):
		"""
		Move to the next state or step in the simulation.
		This method must be implemented by child classes.
		"""
		pass
