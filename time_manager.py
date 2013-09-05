import datetime
import pygame.time

import settings
import state_manager

"""
Time
"""

clock = pygame.time.Clock()

def start():
	global start_time, current_time, frame, offset
	start_time = datetime.datetime.now()
	current_time = start_time
	frame = 0
	offset = 0

def get_time(): return current_time + datetime.timedelta(seconds=offset)
def get_real_time(): return current_time
def get_since(): return get_time() - start_time
def get_real_since(): return get_real_time() - start_time

def tick():
	clock.tick(settings.get('frame rate'))

	global current_time
	current_time = datetime.datetime.now()

	if time_is_paused:
		offset_time(frames=-1)
	else:
		global frame
		frame += 1

def get_clock_string(timedelta=0):
	total_seconds = timedelta.total_seconds()
	clock_string = '-'*(total_seconds<0) + str(datetime.timedelta(seconds=abs(total_seconds)))
	dot = clock_string.index('.')
	if dot: clock_string = clock_string[:dot+2]
	return clock_string

"""
Editable time
"""

def offset_time(seconds=0, frames=0):
	global offset
	offset += seconds
	offset += float(frames)/settings.get('frame rate')
	#utils.log_function_call(offset)
state_manager.add_event_handler(lambda: offset_time(-0.25), '', pygame.K_r)
state_manager.add_event_handler(offset_time, '', event_type=state_manager.EVENT_TIMECHANGE)

time_is_paused = False
def pause_time(seconds=0, frames=0):
	time_is_paused = True
def unpause_time():
	time_is_paused = False
#state_manager.add_event_handler(pause_time, '', pygame.K_p, command_key, event_type=state_manager.EVENT_TIMEPAUSE)

