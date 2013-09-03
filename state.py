import platform
import pygame

import utils  # log_function_call()

"""
Custom event types
"""
EVENT_STATECHANGE = pygame.USEREVENT

"""
Event handlers
"""
event_handlers = []

def add_event_handler(handler, state='', shortcut_key=None, shortcut_mod=pygame.KMOD_NONE, shortcut_up_or_down=pygame.KEYDOWN, event_type=None):
	"""Register a function to handle events and/or keyboard shortcuts.
	User event handlers should have an 'event' parameter.
	Other event handlers should have no required parameters.
	"""
	event_handlers.append((handler, event_type, state, shortcut_key, shortcut_mod, shortcut_up_or_down))

def handle_user_event(event):
	"""Call the handler for a user event and pass it the event data."""
	for h, et, st, sk, sm, sud in event_handlers:
		if st in ['',state] and et==event.type:
			#utils.log_function_call(h.__name__)
			h(event)

"""Platform-independent command key accelerator for keyboard shortcuts."""
command_key = pygame.KMOD_CTRL
if platform.system() == 'Darwin': command_key = pygame.KMOD_META

def keyboard_shortcut(shortcut_up_or_down, shortcut_key, shortcut_mod):
	"""Call the function(s) associated with this keyboard shortcut."""
	for h, et, st, sk, sm, sud in event_handlers:
		if st in ['',state] and sk==shortcut_key and (sm==shortcut_mod or shortcut_mod&sm) and sud==shortcut_up_or_down:
			#utils.log_function_call()
			h()

def handle_event_queue():
	"""Call handlers for the events in the queue."""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
		elif event.type == pygame.VIDEORESIZE:
			resize(event.size)
		elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
			keyboard_shortcut(event.type, event.key, pygame.key.get_mods())
		elif event.type >= pygame.USEREVENT:
			handle_user_event(event)
		elif event.type in [pygame.ACTIVEEVENT, pygame.MOUSEMOTION]:
			pass  # don't print these
		else:
			print 'Ignored event {}'.format(event)

"""Quit handler."""
done = False  # exit flag for game loop
def quit():
	global done
	done = True
add_event_handler(quit, shortcut_key=pygame.K_q, shortcut_mod=command_key, event_type=pygame.QUIT)

"""
States
"""
state = 'menu'  # TODO: start with loading screen
def change_state(event):
	global state
	old_state = state
	state = event.state
	#print 'Changed from state {} to {}.'.format(old_state, state)
add_event_handler(change_state, event_type=EVENT_STATECHANGE)

"""State transition events."""
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='play')), 'menu', pygame.K_SPACE)  # start game -> press SPACE on main menu

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='menu')), 'play', pygame.K_ESCAPE)  # end game (menu) -> press ESC during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='lose')), 'play', pygame.K_l)  # end game (lose) -> press L during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='win')), 'play', pygame.K_w)  # end game (win) -> press W during play

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='menu')), 'lose', pygame.K_ESCAPE)  # return to menu -> press ESC on lose screen
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='menu')), 'win', pygame.K_ESCAPE)  # return to menu -> press ESC on win screen

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='pause')), 'play', pygame.K_p, command_key)  # pause -> press command-P during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, state='play')), 'pause', pygame.K_p, command_key)  # unpause -> press command-P while paused
