import datetime
import random
import pygame

import state

"""
Color
"""
colors = {
	'black': 		[  0,  0,  0],
	'dark gray':	[ 63, 63, 63],
	'medium gray':	[127,127,127],
	'light gray':	[191,191,191],
	'white':		[255,255,255],
	'red':			[255,  0,  0],
	'yellow':		[255,255,  0],
	'green':		[  0,255,  0],
	'cyan':			[  0,255,255],
	'blue':			[  0,  0,255],
	'magenta':		[255,  0,255]
}
frame = 0  # used for color rotation

"""
Settings
"""
settings = {  # default settings, overriden in init()
	'title': 'Title',  # window caption, auto-logo on main menu

	'size': [800, 600],  # window size / fullscreen resolution
	'keep_aspect': True,  # when resizing, keep the current aspect ratio
	'frame_rate': 30,  # maximum frame rate, reduce to limit CPU use

	'background_color': 'black',
	'foreground_color': 'white',
	'title_color': 'foreground_color',

	'pulse_color': 'rotate: black, dark gray, medium gray, light gray, white, white, light gray, medium gray, dark gray, black',
	'panic_color': 'rotate: red, cyan, yellow, magenta, green, blue',
	'color_rotation_speed': 4,  # frames per color

	'default_font': {'name':None, 'scale':1.5, 'aa':True, 'color':'foreground_color'},
	'title_font': {'name':None, 'scale':4},  # TODO: fancy font name
}
settings['mode'] = pygame.DOUBLEBUF  # requires flip() after draw loop
#settings['mode'] |= pygame.FULLSCREEN  # fullscreen
#settings['mode'] |= pygame.NOFRAME  # hide border and controls
#settings['mode'] |= pygame.RESIZABLE  # user can resize window

def init(new_settings):
	"""Initialize pygame with the given settings."""
	settings.update(new_settings)
	pygame.display.set_caption(settings['title'])
	return resize(settings['size'])

def get_color(color_name):
	"""Given a color name, return its RGB values.
	A color name may be:
		an index into colors ('white', 'black')
		an index into settings ('background color')
		an RGB value ([0,255,255])
		a rotate instruction, containing 'rotate: ' followed by a comma-separated list of color names; this will return the next color in the list after every color_rotation_speed frames ('rotate: red, green, blue')
		a random instruction, containing 'random: ' followed by a comma-separated list of color names; this will return a randomly chosen color from the list ('random: red, green, blue')
	"""
	if isinstance(color_name, list):
		return color_name

	if color_name in colors:
		return colors[color_name]

	if color_name in settings:
		return get_color(settings[color_name])

	if color_name[:8] == 'rotate: ':
		rotation = [r.strip(' ') for r in color_name[8:].split(',')]
		crs = settings['color_rotation_speed']
		return get_color(rotation[int(frame/crs) % len(rotation)])

	if color_name[:8] == 'random: ':
		rotation = [r.strip(' ') for r in color_name[8:].split(',')]
		return get_color(random.choice(rotation))

	print 'Unknown color name: {}'.format(color_name)
	return [0,0,0]

def get_font_settings(font_name):
	"""Given a font name in settings, return a dict with all the options for that font."""
	if not font_name in settings:
		print 'Font not found: {}'.format(font_name)
		return None
	font_settings = settings['default_font'].copy()
	font_settings.update(settings[font_name])
	font_settings['size'] = get_font_size(font_settings['scale'])
	return font_settings

def get_font(font_name):
	"""Given a font name in settings, return a pygame Font object.
	Note: Font objects only contain the font face and size. Use get_font_settings() if you also need antialiasing and color."""
	font_settings = get_font_settings(font_name)
	return pygame.font.Font(font_settings['name'], font_settings['size'])

"""
Window size
"""
def resize(new_size):
	"""Resize the window, preserving aspect ratio if settings['keep_aspect'], and return the screen returned by pygame.display.set_mode().
	"""
	settings['size'] = [new_size[1]*settings['size'][0]/settings['size'][1], new_size[1]] if settings['keep_aspect'] else new_size  # size = new*old_x/old_y preserves aspect ratio
	return pygame.display.set_mode(settings['size'], settings['mode'])

"""Shortcuts for top/center/bottom of screen."""
def tx(border=0): return border
def ty(border=0): return border
def cx(border=0): return settings['size'][0]/2
def cy(border=0): return settings['size'][1]/2
def bx(border=0): return settings['size'][0] - border - 1
def by(border=0): return settings['size'][1] - border - 1

"""Shortcut for relative font sizes."""
def get_font_size(scale=1): return int(int(1+settings['size'][1]/40)*scale)  # 16 at 800x600

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
def draw_crosshairs(screen, x, y, color='white', size=1, width=1):
	pygame.draw.line(screen, get_color(color), [x-size, y], [x+size, y], width)
	pygame.draw.line(screen, get_color(color), [x, y-size], [x, y+size], width)

def draw_text(screen, text, x=0, y=0, font_name='default_font', xalign='left', yalign='top', line_spacing=1.0):

	fs = get_font_settings(font_name)
	font = pygame.font.Font(fs['name'], fs['size'])

	lines = text.split('\n')
	renders = [font.render(line, fs['aa'], get_color(fs['color'])) for line in lines]
	width = max([r.get_width() for r in renders])
	line_height = font.get_linesize() * line_spacing
	height = line_height * len(lines)

	container = pygame.surface.Surface((width, height))
	line_y = 0
	for render in renders:
		line_x = 0-get_text_x(container, 0, xalign)
		location = [get_text_x(render, line_x, xalign), line_y]
		container.blit(render, location)
		line_y += line_height

	location = [get_text_x(container, x, xalign), get_text_y(renders[0], y, yalign, font)]
	screen.blit(container, location)

def draw_clock(screen, timedelta):
	total_seconds = timedelta.total_seconds()
	clock_string = '-'*(total_seconds<0) + str(datetime.timedelta(seconds=abs(total_seconds)))
	dot = clock_string.index('.')
	if dot: clock_string = clock_string[:dot+2]
	draw_text(screen, clock_string, cx(), by(50), 'clock_font', 'center', 'baseline')

def draw_fps(screen, fps):
	draw_text(screen, 'fps: {}'.format(fps), bx(10), by(10), 'fps_font', 'right', 'baseline')

"""
The current state's draw routine is called once per frame.
"""
last_frame_letter = 0
def draw_state_intro(screen, since):
	global last_frame_letter

	draw_text(screen, 'Intro', cx(), cy()/4, 'title_font', 'center')

	text = """These are Triggers.
A Trigger has a Warning and an Effect.
The Effect happens ten seconds after the Warning.
This time can not||| be changed.
Time itself||| can||||||||| be changed."""

	start_time = 0
	end_time = 10
	length = end_time - start_time
	doneness = 1 - (length - since.total_seconds()) / length
	letter = int(len(text) * max(min(doneness, 1), 0))

	this_frame_text = text[last_frame_letter:letter]
	if '|' in this_frame_text:
		state.post_event('time change', frames=-1)

	drawable_text = text[:letter].replace('|', '')
	draw_text(screen, drawable_text, cx(), cy()/2, 'default_font', 'center')
	last_frame_letter = letter

def draw_state_menu(screen, since):
	draw_text(screen, settings['title'], cx(), cy()/4, 'title_font', 'center')

def draw_state_game(screen, since):
	if state.state != 'play':
		screen.fill(get_color('dark gray'))

	draw_crosshairs(screen, tx(), ty(), 'medium gray', 4, 1)
	draw_crosshairs(screen, cx(), cy(), 'medium gray', 2, 1)
	draw_crosshairs(screen, bx(), by(), 'medium gray', 4, 1)

	if state.state == 'pause':
		draw_text(screen, 'Pause', cx(), cy()/4, 'title_font', 'center')
	if state.state == 'lose':
		draw_text(screen, 'You Lose', cx(), cy()/4, 'title_font', 'center')
	if state.state == 'win':
		draw_text(screen, 'You Win!', cx(), cy()/4, 'title_font', 'center')

def draw_state_credits(screen, since):
	draw_text(screen, 'Credits', cx(), cy()/4, 'title_font', 'center')
	draw_text(screen, settings['credits'], cx(), cy()/2, 'default_font', 'center')

"""Connect state names and drawing functions. A drawing function may handle more than one state."""
draw_state = {
	'menu': draw_state_intro,
	'play': draw_state_game,
	'pause': draw_state_game,
	'win': draw_state_game,
	'lose': draw_state_game,
	'credits': draw_state_credits
}
