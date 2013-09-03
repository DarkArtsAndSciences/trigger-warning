import pygame
pygame.init()

import utils
import interface
import state

"""
Settings
"""
settings = {
	'title': 'Game Name',
	'size': [800, 600],
	'credits':
"""Programming by My Name
Art by Someone Else
Fonts from http://example.com

Testers:
various
comical
usernames
"""
}
screen = interface.init(settings)

"""
Time
"""
clock = pygame.time.Clock()

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
		interface.frame += 1

		"""Handle events."""
		state.handle_event_queue()

		"""Redraw screen."""
		screen.fill(interface.get_color('background_color'))
		interface.draw_state[state.state](screen, state.state)
		pygame.display.flip()  # required for double buffering

	"""Exit cleanly."""
	pygame.quit()
