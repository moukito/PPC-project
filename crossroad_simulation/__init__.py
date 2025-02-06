"""
Crossroads Traffic Simulation Package

This package manages traffic lights at an intersection, handling both normal and priority traffic.
It includes:
- Traffic light management
- Normal traffic cycling
- Priority vehicle handling

Modules:
- lights: Controls the state of four independent traffic lights.
- coordinator: Manages vehicle movements and priority logic.
- NormalTrafficGen: Generates regular traffic.
- PriorityTrafficGen: Generates priority vehicles.
"""

from .LightColor import LightColor
from .Direction import Direction
from .Lights import TrafficLights
from .Coordinator import Coordinator
from .NormalTrafficGen import NormalTrafficGen
from .PriorityTrafficGen import PriorityTrafficGen
from .TimeManager import TimeManager


__all__ = [
	"LightColor",
	"Direction",
	"TrafficLights",
	"Coordinator",
	"NormalTrafficGen",
	"PriorityTrafficGen",
	"TimeManager",
]
