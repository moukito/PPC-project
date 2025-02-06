"""
Crossroads Traffic Simulation Package

This package manages traffic lights at an intersection, handling both normal and priority traffic.
It includes:
- Traffic light management
- Normal traffic cycling
- Priority vehicle handling
- Inter-process communication using signals and shared memory

Modules:
- lights: Controls the state of four independent traffic lights.
- coordinator: Manages vehicle movements and priority logic.
- normal_traffic_gen: Generates regular traffic.
- priority_traffic_gen: Generates emergency vehicles.
- display: Provides real-time visualization.
- ipc: Handles inter-process communication (queues, shared memory, signals, sockets).
- config: Stores simulation parameters.
"""

from .LightColor import LightColor
from .Direction import Direction
from .Lights import TrafficLights
from .Coordinator import Coordinator
from .NormalTrafficGen import NormalTrafficGen
from .PriorityTrafficGen import PriorityTrafficGen


__all__ = [
	"LightColor",
	"Direction",
	"TrafficLights",
	"Coordinator",
	"NormalTrafficGen",
	"PriorityTrafficGen",
]
