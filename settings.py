import interface_manager
import time_manager
import utils

import random

"""
Colors
"""
colors = {
	'black':		[  0,  0,  0],
	'dark gray':	[ 63, 63, 63],
	'medium gray':	[127,127,127],
	'light gray':	[191,191,191],
	'white':		[255,255,255],
	'red':			[255,  0,  0],
	'yellow':		[255,255,  0],
	'green':		[  0,255,  0],
	'cyan':			[  0,255,255],
	'blue':			[  0,  0,255],
	'magenta':		[255,  0,255],

	'transparent':	[  0,  0,  0,  0],
	'white 50%':	[255,255,255,127]
}

"""
Settings
"""

db = {}

def set(name, value):
	"""Set a setting by name.
	Forces hashing via str(); names that are unhashable AND unstringable will(?) raise an error.
	"""
	try: # is name hashable?
		hash(name)
	except TypeError: # no
		name = str(name) # force it

	db[name] = value

def set_errorprone(name, value):
	"""Set at setting by name, without error correction."""
	db[name] = value

def get(name, default=None):
	"""Get a setting by name.
	Forces hashing via str(); names that are unhashable AND unstringable will(?) raise an error.
	If there is no setting by that name, return the optional default value. If no default value was given, return None.
	"""

	try: # is name hashable?
		hash(name)
	except TypeError: # no
		name = str(name) # force it

	if name in db:
		return db[name]

	return default

def get_errorprone(name):
	"""Get a setting by name, without error correction."""
	return db[name]

def get_color(color_name, alpha=None):
	"""Given a color name, return its RGB values.
	A color name may be:
		an index into colors ('white', 'black')
		an index into settings ('background color')
		an RGB value ([0,255,255])
		a rotate instruction, containing 'rotate: ' followed by a comma-separated list of color names; this will return the next color in the list after every color_rotation_speed frames ('rotate: red, green, blue')
		a random instruction, containing 'random: ' followed by a comma-separated list of color names; this will return a randomly chosen color from the list ('random: red, green, blue')
	"""

	if isinstance(color_name, list):
		if alpha:
			color_name = [color_name[0], color_name[1], color_name[2], alpha]
		return color_name

	if color_name in colors:
		return get_color(colors[color_name], alpha)

	if color_name in db:
		return get_color(db[color_name], alpha)

	if color_name[:8] == 'rotate: ':
		rotation = [r.strip(' ') for r in color_name[8:].split(',')]
		crs = get('color rotation speed', 1)
		which_color = int(time_manager.frame/crs) % len(rotation)
		return get_color(rotation[which_color], alpha)

	if color_name[:8] == 'random: ':
		rotation = [r.strip(' ') for r in color_name[8:].split(',')]
		return get_color(random.choice(rotation), alpha)

	print 'Unknown color name: {}, alpha: {}'.format(color_name, alpha)
	return [127,127,127,255]

def get_font_settings(font_name):
	"""Given a font name in settings, return a dict with all the options for that font."""
	if not font_name in db:
		print 'Font not found: {}'.format(font_name)
		return None
	font_settings = db['default font'].copy()
	font_settings.update(db[font_name])
	font_settings['size'] = interface_manager.get_font_size(font_settings['scale'])
	return font_settings
