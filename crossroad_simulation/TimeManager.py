import time


class TimeManager:
	"""
	Manages configurable time-steps for simulation.
	Allows the user to define a custom time unit dynamically.
	"""

	def __init__(self, mode, time_unit=1):
		"""
		Initialize with a default time unit (e.g., 1 second).

		:param mode: Mode of the time manager ('auto' or 'manual').
		:param time_unit: Length of a single time unit in seconds.
		"""
		self.mode = mode
		self.time_unit = time_unit

	def change_mode(self, mode=None):
		"""
		Change the mode of the time manager.

		:param mode: New mode to set ('auto' or 'manual'). If None, toggles the current mode.
		"""
		if mode is None:
			self.mode = "auto" if self.mode == "manual" else "manual"
		else:
			self.mode = mode

	def set_time_unit(self, time_unit):
		"""
		Update the time unit dynamically.

		:param time_unit: New time unit in seconds.
		:raises ValueError: If the time unit is not a positive value.
		"""
		if time_unit >= 0:
			self.time_unit = time_unit
		else:
			raise ValueError("Time unit must be a positive value.")

	def sleep(self, units=1):
		"""
		Pause execution for a given number of time units.

		:param units: Number of time units to sleep.
		"""
		if self.mode == "auto":
			if self.time_unit > 0:
				time.sleep(units * self.time_unit)
		elif self.mode == "manual":
			input("Press enter to continue...")


if __name__ == "__main__":
	time_manager = TimeManager("manual")
	time_manager.sleep()
	time_manager.sleep()
	time_manager.sleep()
