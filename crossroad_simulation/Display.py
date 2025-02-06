import socket
import curses
from crossroad_simulation.NormalTrafficGen import MAX_VEHICLES_IN_QUEUE

HOST = "localhost"
PORT = 6666

ROAD_WIDTH = 5


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

	stdscr.refresh()

	while True:
		key = stdscr.getch()  # monitor keyboard
		if key == ord('q'):  # pressing 'q' to quit
			break


def get_vehicles_entry():
	"""
    Get vehicle entry (y, x) of 4 directions ["north", "east", "south", "west"]
    """
	return [(0, MAX_VEHICLES_IN_QUEUE + 1), (MAX_VEHICLES_IN_QUEUE + 1, MAX_VEHICLES_IN_QUEUE * 2 + ROAD_WIDTH - 1),
	        (MAX_VEHICLES_IN_QUEUE * 2 + ROAD_WIDTH - 1, MAX_VEHICLES_IN_QUEUE + 3), (MAX_VEHICLES_IN_QUEUE + 3, 0)]


def get_lights():
	"""
    Get light position (y, x) of 4 directions ["north", "east", "south", "west"]
    """
	return [(MAX_VEHICLES_IN_QUEUE - 1, MAX_VEHICLES_IN_QUEUE + 2), (MAX_VEHICLES_IN_QUEUE + 2, MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH)
	(MAX_VEHICLES_IN_QUEUE + ROAD_WIDTH, MAX_VEHICLES_IN_QUEUE + 2), (MAX_VEHICLES_IN_QUEUE + 2, MAX_VEHICLES_IN_QUEUE - 1)]


def next():
	"""
    
    """
	pass


if __name__ == "__main__":
	curses.wrapper(draw)
