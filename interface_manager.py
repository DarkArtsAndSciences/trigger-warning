import math
import pygame
pygame.init()

import boids
import settings
import state_manager
import time_manager
import trigger_manager
import utils

"""
Application window
"""

def init():
	settings.set('title', 'Trigger Warning')  # window caption, auto-logo on main menu
	settings.set('credits', """www.darkartsandsciences.com""")

	settings.set('size', [800, 600])  # window size / fullscreen resolution
	settings.set('keep aspect', True)  # when resizing, keep the current aspect ratio
	settings.set('frame rate', 30)  # maximum frame rate, reduce to limit CPU use

	"""Colors"""
	settings.set('color rotation speed', 4)  # frames per color
	settings.set('background color', 'dark gray')
	settings.set('foreground color', 'light gray')
	settings.set('overlay color', 'white 50%')
	settings.set('chalk color', [255,250,205])
	settings.set('warning color', 'random: red, red, magenta, white')
	settings.set('trigger color', 'random: green, green, blue, white')
	settings.set('dead trigger color', 'blue')
	settings.set('pulse color', 'rotate: black, dark gray, medium gray, light gray, white, white, light gray, medium gray, dark gray, black')
	settings.set('panic color', 'rotate: red, cyan, yellow, magenta, green, blue')

	"""Fonts: Futura, Unispace, Chalkduster, Rabiohead"""

	settings.set('default font', {'name':None, 'scale':1, 'aa':True, 'color':'foreground color'})

	settings.set('title font', {'name':'chalkduster', 'scale':3.5, 'color':'chalk color'})
	settings.set('intro font', {'name':'rabiohead', 'scale':2.5, 'color':'chalk color'})

	settings.set('warning title font', {'name':'chalkduster', 'scale':3, 'color':'warning color'})
	settings.set('warning text font', {'name':'rabiohead', 'scale':2, 'color':'red'})

	settings.set('clock font', {'name':'unispace', 'scale':2})

	settings.set('fps font', {'name':'futura', 'scale':0.85, 'color':'light gray'})
	settings.set('label font', {'name':'futura', 'scale':0.75})

	"""Initialize pygame window."""
	pygame.display.set_caption(settings.get('title'))
	resize(settings.get('size'))

	"""Initialize triggers."""
	visible_triggers = [(cx()/2,cy(), 25, 'trigger color')]

"""
Main game loop, called once per frame
"""
def loop():

	"""Loop until application exit."""
	while state_manager.done == False:

		"""Update time."""
		time_manager.tick(settings.get('frame rate'), state_manager.state)

		"""Create context."""
		current_context = time_manager.get_time_context()

		"""Handle events."""
		state_manager.handle_event_queue(current_context)
		trigger_manager.tick(current_context)
		boids.update_boids()

		"""Redraw window."""
		window.fill(settings.get_color('background color'))
		draw_state[state_manager.state]()
		draw_fps()

		pygame.display.flip()

	"""Exit cleanly."""
	pygame.quit()

"""
Window settings
"""

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

	global left_clock_x, right_clock_x, clock_y, clock_label_y
	fs = settings.get_font_settings('label font')
	font = pygame.font.SysFont(fs['name'], fs['size'])
	offset = 10
	height = font.get_linesize()
	left_clock_x = tx(offset)
	right_clock_x = bx(offset)
	clock_label_y = by(offset)
	clock_y = by(offset+height)

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

def get_text_x(width, x, align):
	if align == 'left':   return x
	if align == 'center': return x - width/2
	if align == 'right':  return x - width

def get_text_y(height, y, align, ascent=None):
	"""Font ascent is only required for 'baseline' alignment."""
	if align == 'top':    return y
	if align == 'center': return y - height/2
	if align == 'baseline':  return y - ascent
	if align == 'bottom':  return y - height

"""
Drawing utilities
"""

def draw_triggers(surface):
	for x,y,r,c in visible_triggers:
		pygame.draw.circle(surface, settings.get_color(c), (x, y), r)

def draw_crosshairs(surface, x, y, color='white', size=1, width=1):
	pygame.draw.line(surface, settings.get_color(color), [x-size, y], [x+size, y], width)
	pygame.draw.line(surface, settings.get_color(color), [x, y-size], [x, y+size], width)

def draw_text(surface, text, x=0, y=0, font_name='default font', xalign='left', yalign='top', line_spacing=1.0, background_color=(0,0,0,0), limit=None):

	fs = settings.get_font_settings(font_name)
	font = pygame.font.SysFont(fs['name'], fs['size'])

	lines = text.split('\n')
	renders = [font.render(line, fs['aa'], settings.get_color(fs['color'])) for line in lines]
	if limit: limited_renders = [font.render(line[:limit], fs['aa'], settings.get_color(fs['color'])) for line in lines]
	width = max([r.get_width() for r in renders])
	line_height = font.get_linesize() * line_spacing
	height = line_height * len(lines)

	xpos = get_text_x(width, x, xalign)
	ypos = get_text_y(renders[0].get_height(), y, yalign, font.get_ascent())
	container = surface.subsurface(xpos, ypos, width, height)

	line_y = 0
	for i, render in enumerate(renders):
		line_x = 0-get_text_x(container.get_width(), 0, xalign)
		location = [get_text_x(render.get_width(), line_x, xalign), line_y]
		container.blit(render, location)
		line_y += line_height

def draw_clock():
	"""Draw two clocks, one for game time and one for real time."""
	game_clock_string = time_manager.get_clock_string()
	real_clock_string = time_manager.get_real_clock_string()
	draw_text(window, game_clock_string, left_clock_x, clock_y, 'clock font', 'left', 'bottom')
	draw_text(window, real_clock_string, right_clock_x, clock_y, 'clock font', 'right', 'bottom')
	draw_text(window, 'game time', left_clock_x, clock_label_y, 'label font', 'left', 'bottom')
	draw_text(window, 'real time', right_clock_x, clock_label_y, 'label font', 'right', 'bottom')

def draw_fps():
	"""Display the current frame rate."""
	fps = time_manager.clock.get_fps()
	fps_string = 'fps: {}'.format(int(fps))
	draw_text(window, fps_string, bx(10), ty(10), 'fps font', 'right', 'top')

def fade(now, start_time, end_time=None, length=10):
	"""Calculate an alpha for fading out from start_time to end_time over length seconds. Returns a float between 0.0 and 1.0; multiply by 255 for a value usable by pygame.
	"""
	if not end_time: end_time = start_time
	if now < start_time: return 0
	if now < end_time: return 1
	if now > end_time + length: return 0
	return 1 - (now-end_time)/length

def get_subsurface(surface, alpha=255, bg='background color'):
	bg = settings.get_color(bg)
	subsurface = pygame.surface.Surface(surface.get_size())
	subsurface.set_alpha(alpha)
	subsurface.set_colorkey(bg)
	subsurface.fill(bg)
	return subsurface

"""
State draw routines

The current state's draw routine is called once per frame.
"""

def draw_state_menu():
	draw_text(window, settings.get('title'), cx(), cy()/3, 'title font', 'center', 'baseline')

last_frame_letter = 0
intro_text = """A Trigger has a Warning and an Effect.||
The Effect occurs ten seconds after the Warning.||
Triggers can not be changed.||||
Time itself|| can not||<<<<||| be changed.||"""
intro_text_length = len(intro_text.replace('|','').replace('<',''))

def draw_state_intro():
	global last_frame_letter, intro_text

	fr = settings.get('frame rate')
	since = time_manager.get_since().total_seconds()

	DEBUG = True
	if DEBUG:
		start_time = 0
		end_time = 2
		fade_time = 1
		pause_multiplier = 1  # one frame pause per |
	else:
		start_time = 0.5
		end_time = 7
		fade_time = 2.5
		pause_multiplier = fr  # one second pause per |
	length = end_time - start_time

	if since > start_time:
		doneness = 1 - (start_time + length - since) / length
		doneness = max(min(doneness, 1), 0)
		letter = int(len(intro_text) * doneness)
		this_frame_text = intro_text[last_frame_letter:letter]

		if since > start_time + end_time + fade_time:
			state_manager.post_event('state change', new_state='play')

		pauses = 0
		if '|' in this_frame_text:
			pauses += this_frame_text.count('|')
			intro_text = intro_text.replace('|','', pauses)
			letter -= pauses
			pauses *= pause_multiplier

		if '<' in this_frame_text:
			"""Remove each < and the letter before it."""
			pauses2 = this_frame_text.count('<')
			for i in xrange(pauses2):
				where = intro_text.find('<')
				first = intro_text[:where-1]
				second = intro_text[where+1:]
				letter -= 2
				intro_text = first + second
			pauses += pauses2  # one frame pause

		if pauses:
			time_manager.pause_time()
			pause_time = 1.0 * pauses * intro_text_length / length / fr / fr
			state_manager.delay_event('time unpause', time_manager.get_real_future_time(pause_time))

		drawable_text = intro_text[:letter]
		last_frame_letter = letter

		alpha = 255*fade(since, start_time, end_time, fade_time)
		surface = get_subsurface(window, alpha)
		draw_text(surface, drawable_text, cx(), cy()/2, 'intro font', 'center', 'center', line_spacing=1.5, limit=letter)
		window.blit(surface, (0, 0))  # TODO: blend mode

	draw_text(window, 'Intro', cx(), cy()/3, 'title font', 'center', 'baseline')
	draw_clock()

def draw_state_game():
	draw_crosshairs(window, tx(), ty(), 'medium gray', 4, 1)
	draw_crosshairs(window, cx(), cy(), 'pulse color', 2, 1)
	draw_crosshairs(window, bx(), by(), 'medium gray', 4, 1)

	for title, text, when in trigger_manager.warning_queue:
		current_context = time_manager.get_time_context()
		alpha = fade(current_context['since'].total_seconds(), when.total_seconds())
		if alpha > 0.0:
			surface = get_subsurface(window, 255*alpha)
			draw_text(surface, title, cx(), cy()/3, 'warning title font', 'center', 'baseline')
			draw_text(surface, text, cx(), cy()*2/3, 'warning text font', 'center', 'bottom')
			window.blit(surface, (0, 0))

	draw_triggers(window)
	boids.draw_boids(window)
	draw_clock()

	if state_manager.state != 'play':
		overlay = pygame.surface.Surface(settings.get('size'), pygame.SRCALPHA)
		overlay.fill(settings.get_color('overlay color'))
		window.blit(overlay, (0, 0))  # TODO: blend mode?

		if state_manager.state == 'pause':
			draw_text(window, 'Pause', cx(), cy()/3, 'title font', 'center', 'baseline')
		if state_manager.state == 'lose':
			draw_text(window, 'You Lose', cx(), cy()/3, 'title font', 'center', 'baseline')
		if state_manager.state == 'win':
			draw_text(window, 'You Win!', cx(), cy()/3, 'title font', 'center', 'baseline')

def draw_state_credits():
	draw_text(window, 'Credits', cx(), cy()/3, 'title font', 'center', 'baseline')
	draw_text(window, settings['credits'], cx(), cy()/2, 'intro font', 'center')

"""Connect state names and drawing functions. A drawing function may handle more than one state."""
draw_state = {
	'menu': draw_state_menu,
	'intro': draw_state_intro,
	'play': draw_state_game,
	'pause': draw_state_game,
	'win': draw_state_game,
	'lose': draw_state_game,
	'credits': draw_state_credits
}
