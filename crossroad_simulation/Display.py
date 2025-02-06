import socket
import curses
from typing import Dict, List
from crossroad_simulation.NormalTrafficGen import MAX_VEHICLES_IN_QUEUE
from crossroad_simulation.Direction import Direction
from crossroad_simulation import Vehicle
from crossroad_simulation.Coordinator import Coordinator

HOST = "localhost"
PORT = 6666
ROAD_WIDTH = 5 # This variable is not modifiable, because we suppose there's only 2 lane for each direction,
               # which means 1 lane for entry and 1 lane for exit
BUFFERSIZE = 1024


def draw(stdscr):
	stdscr.clear()

	size = MAX_VEHICLES_IN_QUEUE * 2 + ROAD_WIDTH

	terminal_height, terminal_width = stdscr.getmaxyx()
	if terminal_height < size + 3 or terminal_width < size + 3:
		err = f"Terminal size is too small, need at least {size + 3} lines for height and width !"
		raise ValueError(err)

	for i in range(size):
		for j in range(size):
			if (MAX_VEHICLES_IN_QUEUE <= i < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH and
					not (MAX_VEHICLES_IN_QUEUE <= j < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH)):
				char = '-' if (i - MAX_VEHICLES_IN_QUEUE) % 2 == 0 else ' '
			elif (MAX_VEHICLES_IN_QUEUE <= j < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH and
			      not (MAX_VEHICLES_IN_QUEUE <= i < MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH)):
				char = '|' if (j - MAX_VEHICLES_IN_QUEUE) % 2 == 0 else ' '
			else:
				char = ' '
			stdscr.addch(i, j, char)

	stdscr.addstr(size + 2, 0, "Press 'q' to quit.")

	print_vehicles(stdscr, None)

    stdscr.refresh()

	while True:
		key = stdscr.getch()  # monitor keyboard
		if key == ord('q'):  # pressing 'q' to quit
			break


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


def get_lights():
	"""
    Get light position of 4 directions
    """
	return {Direction.NORTH:(MAX_VEHICLES_IN_QUEUE - 1, MAX_VEHICLES_IN_QUEUE + 2), Direction.EAST:(MAX_VEHICLES_IN_QUEUE + 2, MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH),
	Direction.SOUTH:(MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH, MAX_VEHICLES_IN_QUEUE + 2), Direction.WEST:(MAX_VEHICLES_IN_QUEUE + 2, MAX_VEHICLES_IN_QUEUE - 1)}


def next():
	"""
    
    """
	pass

def print_vehicles(stdscr, coordinator: Coordinator):
    # Enable color mode
    curses.start_color()

    # Define a color pair (1 = red text on default background)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

    roads = {Direction.NORTH: [Vehicle("normal", Direction.NORTH, Direction.SOUTH),
                               Vehicle("normal", Direction.NORTH, Direction.SOUTH),
                               Vehicle("normal", Direction.NORTH, Direction.WEST),
                               Vehicle("normal", Direction.NORTH, Direction.EAST)]
                               ,
            Direction.EAST: [Vehicle("normal", Direction.EAST, Direction.NORTH),
                             Vehicle("normal", Direction.EAST, Direction.SOUTH),
                             Vehicle("normal", Direction.EAST, Direction.WEST)]
                             ,
            Direction.SOUTH: [Vehicle("priority", Direction.SOUTH, Direction.NORTH)]
            }

    for road in roads.keys():
        write = {Direction.NORTH: 'N', Direction.EAST: 'E', Direction.SOUTH: 'S', Direction.WEST: 'W'}
        for i in range(len(roads[road])):
            y, x = get_vehicles_legal_entry_position()[i]
            if roads[road][i].type == "normal":
                stdscr.addch(y, x, write[road])
            else:
                stdscr.addch(y, x, write[road], curses.color_pair(1)) # mark priority vehicle in blue

def receive_from_coordinator():
    """
    Listens for traffic updates from the Coordinator via a socket.
    Prints received messages in real-time.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the server to the specified IP and port
        server_socket.bind((HOST, PORT))
        server_socket.listen()  # Start listening for incoming connections
        print(f"[Display] Listen traffic updates on {HOST}:{PORT}...")

        conn, addr = server_socket.accept()  # Accept an incoming connection
        with conn:
            print(f"[Display] Connected to Coordinator at {addr}")
            while True:
                try:
                    data = conn.recv(BUFFERSIZE)  # Receive up to 1024 bytes
                    if not data:
                        break  # Stop if no more data is received

                    print(f"[Traffic Update] {data.decode()}")  # Print received message

                except socket.error as e:
                    print(f"[Display] Socket error: {e}")
                    break  # Stop receiving if there's a socket error
if __name__ == "__main__":
	curses.wrapper(draw)