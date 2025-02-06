from enum import Enum


class Direction(Enum):
	"""
	Enum representing the four possible directions at the intersection.
	"""
	NORTH = "north"
	EAST = "east"
	SOUTH = "south"
	WEST = "west"

	@classmethod
	def list(cls):
		"""
		Returns a list of all possible Direction values.

		:return: List of direction values.
		"""
		return [direction.value for direction in cls]

	def __str__(self):
		"""
		String representation of the direction.

		:return: String representation of the direction.
		"""
		return self.value

	def get_right(self):
		"""
		Returns the direction to the right of the current direction.

		:return: Direction to the right.
		"""
		directions = list(Direction)
		index = (directions.index(self) + 1) % len(directions)
		return directions[index]

	def get_left(self):
		"""
		Returns the direction to the left of the current direction.

		:return: Direction to the left.
		"""
		directions = list(Direction)
		index = (directions.index(self) - 1) % len(directions)
		return directions[index]


if __name__ == "__main__":
	print(Direction("north"))
	direction = Direction.NORTH
	print(direction)
	print(direction.get_right())
