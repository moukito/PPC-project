# Crossroad Simulation

## Description
This project simulates traffic at an intersection with normal and priority vehicles. It uses multiprocessing to manage traffic lights, vehicle generation, and coordination between different components.

## Requirements
- Python 3.x
- `sysv_ipc` library
- `curses` library

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/moukito/PPC-project.git
    cd PPC-project
    ```

2. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Simulation
1. Navigate to the project directory:
    ```sh
    cd PPC-project
    ```

2. Run the main script:
    ```sh
    python main.py
    ```

3. To quit the simulation, press `Ctrl+C`.

## Project Structure
- `main.py`: Entry point for the simulation.
- `crossroad_simulation/TimeManager.py`: Manages time steps for the simulation.
- `crossroad_simulation/Direction.py`: Enum for intersection directions.
- `crossroad_simulation/Display.py`: Handles the display of the intersection using curses.
- `crossroad_simulation/LightColor.py`: Enum for traffic light colors.
- `crossroad_simulation/PriorityTrafficGen.py`: Generates priority traffic.
- `crossroad_simulation/NormalTrafficGen.py`: Generates normal traffic.
- `Lights.py`: handle traffic light.
- `Coordinator.py`: manage which vehicle can pass through the crossroad.