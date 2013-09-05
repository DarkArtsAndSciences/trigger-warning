import platform
import pygame

import utils  # log_function_call()

"""
Custom event types
"""

EVENT_STATECHANGE = pygame.USEREVENT + 1
EVENT_TIMECHANGE = pygame.USEREVENT + 2
EVENT_TIMEPAUSE = pygame.USEREVENT + 3
EVENT_TIMEUNPAUSE = pygame.USEREVENT + 4

event_types = {
	'state change': EVENT_STATECHANGE,
	'time change': EVENT_TIMECHANGE,
	'time pause': EVENT_TIMEPAUSE,
	'time unpause': EVENT_TIMEUNPAUSE
}

def get_event_id(name):
	return event_types[name]

"""
Event posting
"""

def post_event(event, **kwargs):
	if isinstance(event, int) and pygame.NOEVENT < int(event) < pygame.NUMEVENTS:
		e = pygame.event.Event(event, kwargs)
	else:
		e = pygame.event.Event(event_types[str(event)], kwargs)
	pygame.event.post(e)
	#utils.log_function_call(e)

delayed_events = []
def delay_event(event, when, **kwargs):
	delayed_events.append((when, event, kwargs))

"""
Event handlers
"""

event_handlers = []

def add_event_handler(handler, state='', shortcut_key=None, shortcut_mod=pygame.KMOD_NONE, shortcut_up_or_down=pygame.KEYDOWN, event_type=None):
	"""Register a function to handle events and/or keyboard shortcuts.
	User event handlers should have an 'event' parameter.
	Other event handlers should have no required parameters.
	TODO: add kwargs and pass them on to events
	"""
	event_handlers.append((handler, event_type, state, shortcut_key, shortcut_mod, shortcut_up_or_down))

def handle_user_event(event):
	"""Call the handler for a user event and pass it the event data."""
	for h, et, st, sk, sm, sud in event_handlers:
		if st in ['',state] and et==event.type:
			#utils.log_function_call(h.__name__)
			h(**event.dict)

"""Platform-independent command key accelerator for keyboard shortcuts."""
command_key = pygame.KMOD_CTRL
if platform.system() == 'Darwin': command_key = pygame.KMOD_META

def keyboard_shortcut(shortcut_up_or_down, shortcut_key, shortcut_mod):
	"""Call the function(s) associated with this keyboard shortcut."""
	for h, et, st, sk, sm, sud in event_handlers:
		if st in ['',state] and sk==shortcut_key and (sm==shortcut_mod or shortcut_mod&sm) and sud==shortcut_up_or_down:
			#utils.log_function_call()
			h()

def handle_event_queue(now):
	"""Call handlers for the events in the pygame event queue."""
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

	"""Post any delayed events whose time is up."""
	for i, (when, event, kwargs) in enumerate(delayed_events):
		if now >= when:
			post_event(event, **kwargs)
			del delayed_events[i]


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

def change_state(new_state):
	global state
	old_state = state
	state = new_state
	#print 'Changed from state {} to {}.'.format(old_state, state)
add_event_handler(change_state, event_type=EVENT_STATECHANGE)

"""
State transition events
"""

#add_event_handler(time_manager.start, 'menu', pygame.K_SPACE)
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='intro')), 'menu', pygame.K_SPACE)  # start game -> press SPACE on main menu

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='menu')), 'play', pygame.K_ESCAPE)  # end game (menu) -> press ESC during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='lose')), 'play', pygame.K_l)  # end game (lose) -> press L during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='win')), 'play', pygame.K_w)  # end game (win) -> press W during play

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='menu')), 'lose', pygame.K_ESCAPE)  # return to menu -> press ESC on lose screen
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='menu')), 'win', pygame.K_ESCAPE)  # return to menu -> press ESC on win screen

add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='pause')), 'play', pygame.K_p, command_key)  # pause -> press command-P during play
add_event_handler(lambda: pygame.event.post(pygame.event.Event(EVENT_STATECHANGE, new_state='play')), 'pause', pygame.K_p, command_key)  # unpause -> press command-P while paused

"""
Game mechanics
"""

def fire():
	print 'fire'
add_event_handler(fire, 'play', pygame.K_SPACE)
