from enum import Enum


class Direction(Enum):
	NORTH = "north"
	SOUTH = "south"
	EAST = "east"
	WEST = "west"

	@classmethod
	def list(cls):
		"""
		Returns a list of all possible Direction values.
		"""
		return [direction.value for direction in cls]

	def __str__(self):
		"""
		String representation of the direction.
		"""
		return self.value
