import datetime
import random
import pygame

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

	'default_font': {'name':None, 'scale':1, 'aa':True},
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
def get_font_size(scale=1): return int(1+settings['size'][1]/40)*scale  # 16 at 800x600

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
	if align == 'bottom':  return y + render.get_height()

"""
Drawing utilities
"""
def draw_title(screen, title):
	font_settings = get_font_settings('title_font')
	title_font = pygame.font.Font(font_settings['name'], font_settings['size'])
	title_render = title_font.render(title, font_settings['aa'], get_color('title_color'))
	title_location = [get_text_x(title_render, cx(), 'center'),
					  get_text_y(title_render, cy()/4, 'center')]
	screen.blit(title_render, title_location)

def draw_crosshairs(screen, x, y, color='white', size=1, width=1):
	pygame.draw.line(screen, get_color(color), [x-size, y], [x+size, y], width)
	pygame.draw.line(screen, get_color(color), [x, y-size], [x, y+size], width)

def draw_clock(screen, timedelta):
	total_seconds = timedelta.total_seconds()
	clock_string = '-'*(total_seconds<0) + str(datetime.timedelta(seconds=abs(total_seconds)))
	dot = clock_string.index('.')
	if dot: clock_string = clock_string[:dot+2]

	font_settings = get_font_settings('clock_font')
	clock_font = pygame.font.Font(font_settings['name'], font_settings['size'])
	clock_render = clock_font.render(clock_string, font_settings['aa'], get_color('clock_color'))
	clock_width = 140  # fixes flicker, TODO: precalc from typical string
	clock_location = [cx()-clock_width/2, by()-50 - clock_font.get_ascent()]
	screen.blit(clock_render, clock_location)

def draw_fps(screen, fps):
	fps_string = "fps: {}".format(fps)
	font_settings = get_font_settings('fps_font')
	fps_font = pygame.font.Font(font_settings['name'], font_settings['size'])
	fps_render = fps_font.render(fps_string, font_settings['aa'], get_color('fps_color'))
	fps_location = [bx(10) - fps_render.get_width(), by(10) - fps_font.get_ascent()]
	screen.blit(fps_render, fps_location)

"""
The current state's draw routine is called once per frame.
"""
def draw_state_menu(screen, state):
	draw_title(screen, settings['title'])

def draw_state_game(screen, state):
	if state != 'play':
		screen.fill(get_color('dark gray'))

	draw_crosshairs(screen, tx(), ty(), 'medium gray', 4, 1)
	draw_crosshairs(screen, cx(), cy(), 'medium gray', 2, 1)
	draw_crosshairs(screen, bx(), by(), 'medium gray', 4, 1)

	if state == 'pause': draw_title(screen, 'Paused')
	if state == 'lose': draw_title(screen, 'You Lose')
	if state == 'win': draw_title(screen, 'You Win')

def draw_state_credits(screen, state):
	draw_title(screen, 'Credits')

"""Connect state names and drawing functions. A drawing function may handle more than one state."""
draw_state = {
	'menu': draw_state_menu,
	'play': draw_state_game,
	'pause': draw_state_game,
	'win': draw_state_game,
	'lose': draw_state_game,
	'credits': draw_state_credits
}
