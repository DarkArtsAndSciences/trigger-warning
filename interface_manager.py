import pygame
pygame.init()

import settings
import state_manager
import time_manager

"""
Application window
"""

def init():
	pygame.display.set_caption(settings.get('title'))
	resize(settings.get('size'))

window = None  # pygame.Surface

window_mode = pygame.DOUBLEBUF  # requires flip() after draw loop
#window_mode |= pygame.FULLSCREEN  # fullscreen
#window_mode |= pygame.NOFRAME  # hide border and controls
#window_mode |= pygame.RESIZABLE  # user can resize window

def resize(new_size):
	"""Resize the window, preserving aspect ratio if settings['keep aspect'], and return the screen returned by pygame.display.set_mode().
	"""
	old_size = settings.get('size')

	if settings.get('keep aspect'):
		aspect_ratio = 1.0*old_size[0]/old_size[1]
		new_size = [int(new_size[1]*aspect_ratio), new_size[1]]

	settings.set('size', new_size)

	global window
	window = pygame.display.set_mode(new_size, window_mode)

"""Shortcuts for top/center/bottom of window."""
def tx(border=0): return border
def ty(border=0): return border
def cx(border=0): return settings.get('size')[0]/2
def cy(border=0): return settings.get('size')[1]/2
def bx(border=0): return settings.get('size')[0] - border - 1
def by(border=0): return settings.get('size')[1] - border - 1

"""Shortcut for relative font sizes."""
def get_font_size(scale=1): return int(int(1+settings.get('size')[1]/40)*scale)  # 16 at 800x600

"""
Text alignment
"""

def get_text_x(render, x, align):
	if align == 'left':   return x
	if align == 'center': return x - render.get_width()/2
	if align == 'right':  return x - render.get_width()

def get_text_y(render, y, align, font=None):
	"""Font is only required for 'baseline' alignment."""
	if align == 'top':    return y
	if align == 'center': return y - render.get_height()/2
	if align == 'baseline':  return y - font.get_ascent()
	if align == 'bottom':  return y - render.get_height()

"""
Drawing utilities
"""

def draw_crosshairs(surface, x, y, color='white', size=1, width=1):
	pygame.draw.line(surface, settings.get_color(color), [x-size, y], [x+size, y], width)
	pygame.draw.line(surface, settings.get_color(color), [x, y-size], [x, y+size], width)

def draw_text(surface, text, x=0, y=0, font_name='default font', xalign='left', yalign='top', line_spacing=1.0, background_color=(0,0,0,0)):

	fs = settings.get_font_settings(font_name)
	font = pygame.font.Font(fs['name'], fs['size'])

	lines = text.split('\n')
	renders = [font.render(line, fs['aa'], settings.get_color(fs['color'])) for line in lines]
	width = max([r.get_width() for r in renders])
	line_height = font.get_linesize() * line_spacing
	height = line_height * len(lines)

	"""Create a container surface filled with the RGBA value in background_color (default: transparent)."""
	container = pygame.surface.Surface((width, height), pygame.SRCALPHA)
	container.fill(background_color)

	line_y = 0
	for render in renders:
		line_x = 0-get_text_x(container, 0, xalign)
		location = [get_text_x(render, line_x, xalign), line_y]
		container.blit(render, location)
		line_y += line_height

	location = [get_text_x(container, x, xalign), get_text_y(renders[0], y, yalign, font)]
	surface.blit(container, location)

def draw_clock(since):
	clock_string = time_manager.get_clock_string(since)
	draw_text(window, clock_string, cx(), by(50), 'clock font', 'center', 'baseline')

def draw_fps(fps):
	fps_string = 'fps: {}'.format(int(fps))
	draw_text(window, fps_string, bx(10), by(10), 'fps font', 'right', 'baseline')

"""
State draw routines

The current state's draw routine is called once per frame.
"""

last_frame_letter = 0
def draw_state_intro(since):
	global last_frame_letter

	draw_text(window, 'Intro', cx(), cy()/4, 'title font', 'center')

	text = """These are Triggers.
A Trigger has a Warning and an Effect.
The Effect happens ten seconds after the Warning.
This time can not| be changed.
Time itself| can||| be changed."""

	start_time = 0
	end_time = 10
	length = end_time - start_time
	doneness = 1 - (length - since.total_seconds()) / length
	letter = int(len(text) * max(min(doneness, 1), 0))

	this_frame_text = text[last_frame_letter:letter]
	if '|' in this_frame_text:
		state_manager.post_event('time pause', seconds=-1)
		# TODO: is this working?

	drawable_text = text[:letter].replace('|', '')
	draw_text(window, drawable_text, cx(), cy()/2, 'default font', 'center')
	last_frame_letter = letter

	draw_crosshairs(window, cx(), cy(), 'pulse color', 2, 1)

def draw_state_menu(since):
	draw_text(window, settings.get('title'), cx(), cy()/4, 'title font', 'center')

def draw_state_game(since):
	draw_crosshairs(window, tx(), ty(), 'medium gray', 4, 1)
	draw_crosshairs(window, cx(), cy(), 'pulse color', 2, 1)
	draw_crosshairs(window, bx(), by(), 'medium gray', 4, 1)

	draw_clock(since)
	# TODO: draw_clock(since_raw)

	if state_manager.state != 'play':
		overlay = pygame.surface.Surface(settings.get('size'), pygame.SRCALPHA)
		overlay.fill(settings.get_color('overlay color'))
		window.blit(overlay, (0, 0))

		if state_manager.state == 'pause':
			draw_text(window, 'Pause', cx(), cy()/4, 'title font', 'center')
		if state_manager.state == 'lose':
			draw_text(window, 'You Lose', cx(), cy()/4, 'title font', 'center')
		if state_manager.state == 'win':
			draw_text(window, 'You Win!', cx(), cy()/4, 'title font', 'center')

def draw_state_credits(since):
	draw_text(window, 'Credits', cx(), cy()/4, 'title font', 'center')
	draw_text(window, settings['credits'], cx(), cy()/2, 'default font', 'center')

"""Connect state names and drawing functions. A drawing function may handle more than one state."""
draw_state = {
	'menu': draw_state_menu,
	'play': draw_state_game,
	'pause': draw_state_game,
	'win': draw_state_game,
	'lose': draw_state_game,
	'credits': draw_state_credits
}

"""
Main game loop, called once per frame
"""
def start():

	"""Loop until application exit."""
	while state_manager.done == False:

		"""Update time."""
		time_manager.tick()
		since = time_manager.get_since()
		fps = time_manager.clock.get_fps()

		"""Handle events."""
		state_manager.handle_event_queue(since)

		"""Redraw window."""
		window.fill(settings.get_color('background color'))
		draw_state[state_manager.state](since)
		draw_fps(fps)

		# TODO: if mode includes double buffering
		pygame.display.flip()  # required for double buffering

	"""Exit cleanly."""
	pygame.quit()
