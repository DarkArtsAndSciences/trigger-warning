import math
import platform
import time

class Warning:
	def __init__(self, string, since):
		self.string = string
		self.since = since

	def __str__(self):
		return warning_string

	def draw(self, fade, screen):
		render = warning_font.render(self.string, warning_aa, warning_color)
		location = [center[0] - render.get_width()/2, center[1] - warning_font.get_ascent()]
		surface = pygame.surface.Surface((render.get_width(), render.get_height()))
		surface.set_alpha(255*fade)
		surface.blit(render, (0,0))
		screen.blit(surface, location)

import pygame
pygame.init()

# colors
black = [  0,  0,  0]
gray  = [127,127,127]
white = [255,255,255]
blue  = [  0,  0,255]
green = [  0,255,  0]
red   = [255,  0,  0]

# settings
frame_rate = 30
size = [800, 600]
center = [400, 300]
screen = pygame.display.set_mode(size)

title = "Trigger Warning"
pygame.display.set_caption(title)

command_key = pygame.KMOD_CTRL
if platform.system() == 'Darwin': command_key = pygame.KMOD_META

background_color = black

warning_font  = pygame.font.Font(None, 72)
fps_font      = pygame.font.Font(None, 14)
clock_font    = pygame.font.Font(None, 72)
intro_font    = pygame.font.Font(None, 36)
warning_aa    = True  # text antialiasing
fps_aa        = True
clock_aa      = True
intro_aa      = True
warning_color = red
fps_color     = white
clock_color   = white
intro_color   = white

# intro / help
letters_per_second = 12
one_second_pause = " "*letters_per_second
intro_time = 20
intro_strings = ["A Trigger has a Warning and an Effect."+one_second_pause,
	"The Effect occurs ten seconds after the Warning."+one_second_pause,
	"Triggers can not be changed."+one_second_pause,
	"Time itself can be changed."]
line_spacing = 1.5

# warnings
warnings = [Warning("Warning!", intro_time+2)]

# loop until quit
done = False
start = time.time()
offset = 0
clock = pygame.time.Clock()
while done == False:

	# limit frame rate and cpu usage
	clock.tick(frame_rate)

	# game time
	now = time.time() + offset
	since = now - start

	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.KEYDOWN:
			if pygame.key.get_mods() & command_key:
				if event.key == pygame.K_q:  # quit
					done = True
			else:
				if event.key == pygame.K_r:  # rewind
					offset -= 0.25

	# draw
	def fade(show_since, fade_since=None, fade_length=10):
		if not fade_since: fade_since = show_since
		if since < show_since: return 0
		if since < fade_since: return 1
		if since > fade_since + fade_length: return 0
		return 1 - (since-fade_since)/fade_length

	# background
	screen.fill(background_color)

	# intro
	if (since < intro_time):
		letters = int(since * letters_per_second)
		i = 0
		used = 0
		while (i < len(intro_strings) and used + len(intro_strings[i]) < letters):
			try: used += len(intro_strings[i])
			except IndexError: break
			i += 1
		intro_surface = pygame.surface.Surface((size[0], size[1]))
		intro_surface.set_alpha(255*fade(0, intro_time-1, 1))
		j = 0
		try: strings = intro_strings[:i] + [intro_strings[i][:letters-used]]
		except IndexError: strings = intro_strings
		for string in strings:
			string_render = intro_font.render(string, intro_aa, intro_color)
			string_location = [100, 100 + j*intro_font.get_linesize()*line_spacing]
			intro_surface.blit(string_render, string_location)
			j += 1
		screen.blit(intro_surface, (0,0))

	# warnings, center
	for warning in warnings:
		fade = fade(warning.since)
		if 0 < fade <= 1: warning.draw(fade, screen)

	# clock, bottom center
	minutes = int(math.floor(since/60))
	sign = "-"*(minutes < 0)
	seconds = abs(int(math.floor(since)%60))
	seconds_zero = "0"*(seconds < 10)
	tenths = int(since*10%10)
	clock_string = "{}{}:{}{}.{}".format(sign, abs(minutes), seconds_zero, seconds, tenths)
	clock_render = clock_font.render(clock_string, clock_aa, clock_color)
	clock_width = 140  # fixes flicker, TODO: precalc from typical string
	clock_location = [center[0]-clock_width/2, size[1]-50 - clock_font.get_ascent()]
	screen.blit(clock_render, clock_location)

	# fps, bottom right
	fps_string = "fps: {}".format(int(clock.get_fps()))
	fps_render = fps_font.render(fps_string, fps_aa, fps_color)
	fps_location = [size[0]-10 - fps_render.get_width(), size[1]-10 - fps_font.get_ascent()]
	screen.blit(fps_render, fps_location)

	# central crosshairs  TODO: follow mouse?
	pygame.draw.line(screen, white, [center[0]-10, center[1]], [center[0]+10, center[1]], 1)
	pygame.draw.line(screen, white, [center[0], center[1]-10], [center[0], center[1]+10], 1)

	pygame.display.flip()

# quit
pygame.quit()
