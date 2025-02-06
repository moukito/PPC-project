import socket
import time
import curses
import threading
from crossroad_simulation.NormalTrafficGen import MAX_VEHICLES_IN_QUEUE
from crossroad_simulation.Direction import Direction
from crossroad_simulation.Coordinator import Coordinator
from crossroad_simulation.LightColor import LightColor

HOST = "localhost"
PORT = 6666
ROAD_WIDTH = 5
BUFFERSIZE = 1024


def get_vehicles_entry():
    """
    Get vehicle entry position of 4 directions
    """
    return {Direction.NORTH: (0, MAX_VEHICLES_IN_QUEUE+1),
            Direction.EAST: (MAX_VEHICLES_IN_QUEUE+1, MAX_VEHICLES_IN_QUEUE*2+ROAD_WIDTH-1),
            Direction.SOUTH: (MAX_VEHICLES_IN_QUEUE*2+ROAD_WIDTH-1, MAX_VEHICLES_IN_QUEUE+3),
            Direction.WEST: (MAX_VEHICLES_IN_QUEUE+3, 0)}


def get_vehicles_legal_entry_position():
    """
    Get vehivles legal entry positions of 4 directions sorted by the closest to the light to the
    farthest from the light
    """
    return {Direction.NORTH: [(i, MAX_VEHICLES_IN_QUEUE+1) for i in range(MAX_VEHICLES_IN_QUEUE-1, -1, -1)],
            Direction.EAST: [(MAX_VEHICLES_IN_QUEUE+1, MAX_VEHICLES_IN_QUEUE+ROAD_WIDTH+i) for i in range(MAX_VEHICLES_IN_QUEUE)],
            Direction.SOUTH: [(MAX_VEHICLES_IN_QUEUE+ROAD_WIDTH+i, MAX_VEHICLES_IN_QUEUE+3) for i in range(MAX_VEHICLES_IN_QUEUE)],
            Direction.WEST: [(MAX_VEHICLES_IN_QUEUE+3, i) for i in range(MAX_VEHICLES_IN_QUEUE-1, -1, -1)]}


def get_vehivles_legal_exit_position():
    """
    Get vehivles legal exit positions of 4 directions sorted by the closest to the light to the
    farthest from the light
    """
    pass


def get_lights_position():
    """
    Get light position of 4 directions
    """
    return {Direction.NORTH: (MAX_VEHICLES_IN_QUEUE-1, MAX_VEHICLES_IN_QUEUE+2),
            Direction.EAST: (MAX_VEHICLES_IN_QUEUE+2, MAX_VEHICLES_IN_QUEUE+ROAD_WIDTH),
            Direction.SOUTH: (MAX_VEHICLES_IN_QUEUE+ROAD_WIDTH, MAX_VEHICLES_IN_QUEUE+2),
            Direction.WEST: (MAX_VEHICLES_IN_QUEUE+2, MAX_VEHICLES_IN_QUEUE-1)}


def next():
    pass


def print_vehicles(stdscr, coordinator: Coordinator):
    curses.start_color()

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    write = {Direction.NORTH: 'N', Direction.EAST: 'E', Direction.SOUTH: 'S', Direction.WEST: 'W'}

    for source, vehicles in coordinator.roads.items():
        for i in range(len(vehicles)):
            y, x = get_vehicles_legal_entry_position()[source][i]
            if vehicles[i].type == "normal":
                stdscr.addch(y, x, write[source])
            else:
                stdscr.addch(y, x, write[source], curses.color_pair(1))


def print_lights(stdscr, coordinator: Coordinator):
    curses.start_color()

    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    for source, light in coordinator.lights_state.items():
        y, x = get_lights_position()[source]
        if light == LightColor.RED.value:
            stdscr.addch(y, x, 'R', curses.color_pair(2))
        else:
            stdscr.addch(y, x, 'G', curses.color_pair(3))


def draw(stdscr, coordinator: Coordinator):
    stdscr.nodelay(True)
    stdscr.clear()

    size = MAX_VEHICLES_IN_QUEUE * 2 + ROAD_WIDTH

    terminal_height, terminal_width = stdscr.getmaxyx()
    if terminal_height < size + 3 or terminal_width < size + 3:
        err = f"Terminal size is too small, need at least {size + 3} lines for height and width !"
        raise ValueError(err)

    while True:
        stdscr.clear()

        for i in range(size):
            for j in range(size):
                if MAX_VEHICLES_IN_QUEUE <= i < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH and not (MAX_VEHICLES_IN_QUEUE <= j < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH):
                    char = '-' if (i - MAX_VEHICLES_IN_QUEUE) % 2 == 0 else ' '
                elif (MAX_VEHICLES_IN_QUEUE <= j < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH and
                    not (MAX_VEHICLES_IN_QUEUE <= i < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH)):
                    char = '|' if (j - MAX_VEHICLES_IN_QUEUE) % 2 == 0 else ' '
                else:
                    char = ' '
                stdscr.addch(i, j, char)

        print_vehicles(stdscr, coordinator)
        print_lights(stdscr, coordinator)

        stdscr.addstr(size + 2, 0, "Press 'q' to quit.")
        stdscr.refresh()

        time.sleep(0.5)

        key = stdscr.getch()
        if key == ord('q'):
            break


def receive_from_coordinator(coordinator: Coordinator):
    """
    Continuously receives traffic updates from Coordinator via a socket 
    and updates the Coordinator object in real-time.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[Display] Listening for traffic updates on {HOST}:{PORT}...")

        conn, addr = server_socket.accept()
        with conn:
            print(f"[Display] Connected to Coordinator at {addr}")
            while True:
                try:
                    data = conn.recv(BUFFERSIZE)
                    if not data:
                        break

                    decoded_data = data.decode()
                    print(f"[Traffic Update] {decoded_data}")

                    update_coordinator_state(coordinator, decoded_data)

                except socket.error as e:
                    print(f"[Display] Socket error: {e}")
                    break


def update_coordinator_state(coordinator: Coordinator, data: str):
    """
    Parses received data and updates the Coordinator object.
    Expected format: "direction: NORTH, light: RED, vehicles: 3"
    """
    parts = data.split(", ")
    state_update = {}

    for part in parts:
        key, value = part.split(": ")
        state_update[key.strip()] = value.strip()

    direction = Direction[state_update["direction"]]
    coordinator.lights_state[direction] = LightColor[state_update["light"]]
    coordinator.roads[direction] = ["Vehicle"] * int(state_update["vehicles"])

    print(f"[Updated] {direction} -> Light: {coordinator.lights_state[direction]}, Vehicles: {len(coordinator.roads[direction])}")


def run_display(coordinator: Coordinator):
    """
    Runs the Display with curses while receiving updates from Coordinator.
    """
    threading.Thread(target=receive_from_coordinator, args=(coordinator,), daemon=True).start()

    curses.wrapper(lambda stdscr: draw(stdscr, coordinator))
