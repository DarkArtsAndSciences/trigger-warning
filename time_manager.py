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
def get_real_future_time(seconds):
	return get_real_time() + datetime.timedelta(seconds=seconds)

def tick():
	clock.tick(settings.get('frame rate'))

	global current_time
	last_time = current_time
	current_time = datetime.datetime.now()
	frame_time = 0 - (current_time - last_time).total_seconds()

	if time_is_paused:
		offset_time(seconds=frame_time)
	else:
		global frame
		frame += 1

def get_delta_string(timedelta=0):
	total_seconds = timedelta.total_seconds()
	clock_string = '-'*(total_seconds<0) + str(datetime.timedelta(seconds=abs(total_seconds)))
	dot = clock_string.index('.')
	if dot: clock_string = clock_string[:dot+2]
	return clock_string

def get_clock_string(): return get_delta_string(get_since())
def get_real_clock_string(): return get_delta_string(get_real_since())

"""
Editable time
"""

def offset_time(seconds=0, frames=0):
	global offset
	offset += seconds
	offset += float(frames)/settings.get('frame rate')
state_manager.add_event_handler(lambda: offset_time(-1), '', pygame.K_r)
state_manager.add_event_handler(offset_time, '', event_type=state_manager.get_event_id('time change'))

time_is_paused = False
def pause_time(seconds=0, frames=0):
	global time_is_paused
	time_is_paused = True
state_manager.add_event_handler(pause_time, event_type=state_manager.get_event_id('time pause'))
def unpause_time():
	global time_is_paused
	time_is_paused = False
state_manager.add_event_handler(unpause_time, event_type=state_manager.get_event_id('time unpause'))

