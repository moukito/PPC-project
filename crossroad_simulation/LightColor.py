from enum import Enum


class LightColor(Enum):
	"""
	Enum representing the possible colors of a traffic light.
	"""
	RED = 0
	GREEN = 1

	def __str__(self):
		"""
		String representation of the light color.

		:return: Capitalized name of the light color.
		"""
		return self.name.capitalize()
