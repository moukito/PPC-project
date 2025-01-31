import os
import unittest
import time
import multiprocessing
import signal
from crossroad_simulation import TrafficLights, RED, GREEN, DIRECTIONS


class TestTrafficLights(unittest.TestCase):

	def setUp(self):
		"""Initialize the traffic light system before each test."""
		self.traffic_lights = TrafficLights()
		self.traffic_lights.start()
		time.sleep(1)  # Give the process some time to start

	def tearDown(self):
		"""Terminate the traffic light process after each test."""
		self.traffic_lights.terminate()
		self.traffic_lights.join()

	def test_initial_state(self):
		"""Check that all lights start as RED."""
		for direction in DIRECTIONS:
			self.assertEqual(self.traffic_lights.lights_state[direction].value, RED,
							 f"Light for {direction} should initially be RED.")

	def test_normal_cycle(self):
		"""Test that the normal cycle alternates between North-South and East-West every 10 seconds."""
		time.sleep(12)  # Wait for a full cycle to switch

		ns_state = self.traffic_lights.lights_state["North"].value
		ew_state = self.traffic_lights.lights_state["East"].value

		self.assertEqual(ns_state, GREEN if ew_state == RED else RED,
						 "North-South and East-West should always have opposite states.")

		time.sleep(12)  # Wait for the next switch

		ns_state = self.traffic_lights.lights_state["North"].value
		ew_state = self.traffic_lights.lights_state["East"].value

		self.assertEqual(ns_state, GREEN if ew_state == RED else RED,
						 "North-South and East-West should have switched states.")

	def test_priority_vehicle(self):
		"""Test that a priority vehicle turns one specific light green while all others turn red."""
		self.traffic_lights.set_priority_direction("West")  # Set priority vehicle coming from West
		os.kill(self.traffic_lights.pid, signal.SIGUSR1)  # Simulate priority vehicle signal

		time.sleep(1)  # Give time for priority mode to activate

		# Check that only the West light is GREEN
		for direction in DIRECTIONS:
			expected_state = GREEN if direction == "West" else RED
			self.assertEqual(self.traffic_lights.lights_state[direction].value, expected_state,
							 f"Light for {direction} should be {'GREEN' if expected_state == GREEN else 'RED'}.")

	def test_priority_vehicle_multiple_directions(self):
		"""Test that priority mode correctly updates for different incoming directions."""
		for direction in ["North", "South", "East", "West"]:
			self.traffic_lights.set_priority_direction(direction)
			os.kill(self.traffic_lights.pid, signal.SIGUSR1)

			time.sleep(1)  # Allow time for state change

			# Check that only the correct light is GREEN
			for dir_check in DIRECTIONS:
				expected_state = GREEN if dir_check == direction else RED
				self.assertEqual(self.traffic_lights.lights_state[dir_check].value, expected_state,
								 f"Light for {dir_check} should be {'GREEN' if expected_state == GREEN else 'RED'}.")


if __name__ == "__main__":
	unittest.main()
