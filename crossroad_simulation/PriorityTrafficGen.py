import multiprocessing

from NormalTrafficGen import NormalTrafficGen
from crossroad_simulation import TrafficLights
from crossroad_simulation.TimeManager import TimeManager


class PriorityTrafficGen(NormalTrafficGen):
	def __init__(self, traffic_event, coordinator_event, queue_event: multiprocessing.Event, traffic_lights: TrafficLights, traffic_queues, time_manager=TimeManager("auto", 0)):
		NormalTrafficGen.__init__(self, traffic_event, coordinator_event, queue_event, traffic_lights, traffic_queues, time_manager)
