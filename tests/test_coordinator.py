import unittest
import time
import multiprocessing
import signal
from Coordinator import Coordinator
from Lights import TrafficLights, RED, GREEN, DIRECTIONS
from ipc import setup_ipc

class TestCoordinator(unittest.TestCase):

	def setUp(self):
		"""Initialize the traffic light system and coordinator before each test."""
		self.traffic_lights = TrafficLights()
		self.traffic_queues = setup_ipc()
		self.coordinator = Coordinator(self.traffic_lights)

		# Start the traffic lights and coordinator as separate processes
		self.lights_process = self.traffic_lights.start()
		self.coordinator_process = self.coordinator.start()

		time.sleep(1)  # Give the processes some time to start

	def tearDown(self):
		"""Terminate all processes and clean up after each test."""
		self.lights_process.terminate()
		self.lights_process.join()
		self.coordinator_process.terminate()
		self.coordinator_process.join()

	def test_normal_traffic_handling(self):
		"""Test that normal vehicles move only when the light is green."""
		# Add a normal vehicle to the North queue
		self.traffic_queues["North"].put({"type": "car", "priority": False})

		time.sleep(12)  # Wait for light cycle (ensure North gets green at some point)

		ns_light_state = self.traffic_lights.lights_state["North"].value
		if ns_light_state == GREEN:
			self.assertFalse(self.traffic_queues["North"].is_empty(),
			                 "Normal vehicle from North should have moved when the light was green.")

	def test_priority_vehicle_handling(self):
		"""Test that a priority vehicle triggers an immediate light change."""
		self.traffic_queues["West"].put({"type": "ambulance", "priority": True})  # Priority vehicle from West

		time.sleep(1)  # Give time for coordinator to detect priority vehicle
		self.lights_process.send_signal(signal.SIGUSR1)  # Simulate priority signal

		time.sleep(1)  # Allow time for light change

		# Verify only the West light is green
		for direction in DIRECTIONS:
			expected_state = GREEN if direction == "West" else RED
			self.assertEqual(self.traffic_lights.lights_state[direction].value, expected_state,
			                 f"Light for {direction} should be {'GREEN' if expected_state == GREEN else 'RED'}.")

	def test_priority_vehicle_multiple_directions(self):
		"""Ensure that different priority vehicles correctly update the green light."""
		for direction in ["North", "South", "East", "West"]:
			self.traffic_queues[direction].put({"type": "firetruck", "priority": True})
			time.sleep(1)  # Allow coordinator to detect priority vehicle
			self.lights_process.send_signal(signal.SIGUSR1)  # Simulate priority signal

			time.sleep(1)  # Allow time for light change

			# Verify only the correct light is green
			for dir_check in DIRECTIONS:
				expected_state = GREEN if dir_check == direction else RED
				self.assertEqual(self.traffic_lights.lights_state[dir_check].value, expected_state,
				                 f"Light for {dir_check} should be {'GREEN' if expected_state == GREEN else 'RED'}.")
