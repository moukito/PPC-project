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

from .Lights import TrafficLights, RED, GREEN, DIRECTIONS
from .Coordinator import Coordinator
#from .normal_traffic_gen import NormalTrafficGenerator
#from .priority_traffic_gen import PriorityTrafficGenerator
#from .display import Display
#from .ipc import setup_ipc, cleanup_ipc
#from .config import SIMULATION_SETTINGS

__all__ = [
	"TrafficLights",
	"Coordinator",
	"NormalTrafficGenerator",
	"PriorityTrafficGenerator",
	"Display",
	"setup_ipc",
	"cleanup_ipc",
	"SIMULATION_SETTINGS",
	"RED",
	"GREEN",
	"DIRECTIONS"
]
