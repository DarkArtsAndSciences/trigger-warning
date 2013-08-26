import math
import platform
import time

class Warning:
	def __init__(self, warning_string):
		self.warning_string = warning_string

	def __str__(self):
		return warning_string

	def draw(self, since, screen):
		warning_fade = (10-since)/10
		warning_render = warning_font.render(self.warning_string, warning_aa, warning_color)
		warning_location = [center[0] - warning_render.get_width()/2, center[1] - warning_font.get_ascent()]
		warning_surface = pygame.surface.Surface((warning_render.get_width(), warning_render.get_height()))
		warning_surface.set_alpha(255*warning_fade)
		warning_surface.blit(warning_render, (0, 0))
		screen.blit(warning_surface, warning_location)

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
warning_aa    = True  # text antialiasing
fps_aa        = True
clock_aa      = True
warning_color = red
fps_color     = white
clock_color   = white

# warnings
warnings = [Warning("Warning!")]

# loop until quit
done = False
start = time.time()
offset = 0
clock = pygame.time.Clock()
while done == False:

	# limit frame rate and cpu usage
	clock.tick(frame_rate)
	now = time.time()
	since = now - start + offset
	#print since

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
					offset -= 1

	# draw
	screen.fill(background_color)

	pygame.draw.line(screen, white, [center[0]-10, center[1]], [center[0]+10, center[1]], 1)
	pygame.draw.line(screen, white, [center[0], center[1]-10], [center[0], center[1]+10], 1)

	for warning in warnings: warning.draw(since, screen)

	fps_string = "fps: {}".format(int(clock.get_fps()))
	fps_render = fps_font.render(fps_string, fps_aa, fps_color)
	fps_location = [size[0]-10 - fps_render.get_width(), size[1]-10 - fps_font.get_ascent()]
	screen.blit(fps_render, fps_location)

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

	pygame.display.flip()

# quit
pygame.quit()
