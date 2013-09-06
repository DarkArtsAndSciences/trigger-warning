import platform
import pygame

import time_manager
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

def add_event_handler(handler, state='', shortcut_key=None, shortcut_mod=pygame.KMOD_NONE, shortcut_up_or_down=pygame.KEYDOWN, event_type=None, **kwargs):
	"""Register a function to handle events and/or keyboard shortcuts."""
	event_handlers.append((handler, event_type, state, shortcut_key, shortcut_mod, shortcut_up_or_down, kwargs))

def handle_user_event(event):
	"""Call the handler for a user event and pass it the event data."""
	for h, et, st, sk, sm, sud, kwargs in event_handlers:
		if st in ['',state] and et==event.type:
			#utils.log_function_call(h.__name__)
			if kwargs: event.dict.update(kwargs)
			h(**event.dict)

"""Platform-independent command key accelerator for keyboard shortcuts."""
command_key = pygame.KMOD_CTRL
if platform.system() == 'Darwin': command_key = pygame.KMOD_META

def keyboard_shortcut(shortcut_up_or_down, shortcut_key, shortcut_mod):
	"""Call the function(s) associated with this keyboard shortcut."""
	for h, et, st, sk, sm, sud, kwargs in event_handlers:
		if st in ['',state] and sk==shortcut_key and (sm==shortcut_mod or shortcut_mod&sm) and sud==shortcut_up_or_down:
			#utils.log_function_call()
			h(**kwargs)

def handle_event_queue(current_context):
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
		if current_context['real now'] >= when:
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

state = 'menu'

def change_state(new_state):
	global state
	old_state = state
	state = new_state
	#print 'Changed from state {} to {}.'.format(old_state, state)

	if state == 'intro':
		time_manager.start()

add_event_handler(change_state, event_type=get_event_id('state change'))

"""
State transition events
"""

#add_event_handler(time_manager.start, 'menu', pygame.K_SPACE)
add_event_handler(post_event, 'menu', pygame.K_SPACE, event='state change', new_state='intro')  # start game -> press SPACE on main menu

add_event_handler(post_event, 'play', pygame.K_ESCAPE, event='state change', new_state='menu')  # end game (menu) -> press ESC during play
add_event_handler(post_event, 'play', pygame.K_l, event='state change', new_state='lose')  # end game (lose) -> press L during play
add_event_handler(post_event, 'play', pygame.K_w, event='state change', new_state='win')  # end game (win) -> press W during play

add_event_handler(post_event, 'lose', pygame.K_ESCAPE, event='state change', new_state='menu')  # return to menu -> press ESC on lose screen
add_event_handler(post_event, 'win', pygame.K_ESCAPE, event='state change', new_state='menu')  # return to menu -> press ESC on win screen

add_event_handler(post_event, 'play', pygame.K_p, command_key, event='state change', new_state='pause')  # pause -> press command-P during play
add_event_handler(post_event, 'pause', pygame.K_p, command_key, event='state change', new_state='play')  # unpause -> press command-P while paused

add_event_handler(lambda: time_manager.offset_time(-1), '', pygame.K_r)
add_event_handler(time_manager.offset_time, '', event_type=get_event_id('time change'))

add_event_handler(time_manager.pause_time, event_type=get_event_id('time pause'))
add_event_handler(time_manager.unpause_time, event_type=get_event_id('time unpause'))


"""
Game mechanics
"""

def fire():
	print 'fire'
add_event_handler(fire, 'play', pygame.K_SPACE)
