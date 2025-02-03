from enum import Enum


class LightColor(Enum):
	RED = 0
	GREEN = 1

	def __str__(self):
		"""
		String representation of the light color.
		"""
		return self.name.capitalize()
