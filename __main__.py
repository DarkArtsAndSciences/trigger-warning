import datetime
import math

import pygame
pygame.init()

import utils
import interface
import state

"""
Settings
"""
settings = {
	'title': 'Trigger Warning',

	'size': [800, 600],
	'trigger_size': 20,

	'background_color': 'black',
	'foreground_color': 'white',
	'live_trigger_color': 'green',
	'dead_trigger_color': 'blue',
	'warning_color': 'red',

	'clock_font': {'scale':4},
	'clock_color': 'yellow',
	'fps_font': {'scale':1},
	'fps_color': 'yellow',

	'credits': """www.darkartsandsciences.com"""
}
screen = interface.init(settings)

"""
Time
"""
clock = pygame.time.Clock()

start_time = datetime.datetime.now()
current_time = start_time
def get_time(): return current_time + datetime.timedelta(seconds=offset)
def get_real_time(): return current_time
def get_since(): return get_time() - start_time
def get_real_since(): return get_real_time() - start_time

offset = 0
def offset_time(seconds=0, frames=0):
	global offset
	offset += seconds
	offset += float(frames)/interface.settings['frame_rate']
	#utils.log_function_call(offset)

state.add_event_handler(lambda: offset_time(-0.25), '', pygame.K_r)
state.add_event_handler(offset_time, '', event_type=state.EVENT_TIMECHANGE)

"""
Game mechanics
"""
def fire():
	print 'fire'
state.add_event_handler(fire, 'play', pygame.K_SPACE)

"""
Main game loop, called once per frame
"""
if __name__ == "__main__":
	while state.done == False:
		"""Update time."""
		clock.tick(interface.settings['frame_rate'])
		current_time = datetime.datetime.now()
		interface.frame += 1

		"""Handle events."""
		state.handle_event_queue()

		"""Redraw screen."""
		screen.fill(interface.get_color('background_color'))
		interface.draw_state[state.state](screen, get_since())
		interface.draw_clock(screen, get_since())
		interface.draw_fps(screen, int(clock.get_fps()))
		pygame.display.flip()  # required for double buffering

	"""Exit cleanly."""
	pygame.quit()
