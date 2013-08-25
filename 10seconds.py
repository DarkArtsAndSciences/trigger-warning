import platform

import pygame
pygame.init()

# colors
black = [  0,  0,  0]
white = [255,255,255]
blue =  [  0,  0,255]
green = [  0,255,  0]
red =   [255,  0,  0]

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

warning_font = pygame.font.Font(None, 72)
warning_aa = True  # text antialiasing
warning_color = red
warning_location = [400, 300]

# loop until quit
done = False
clock = pygame.time.Clock()
while done == False:

	# limit frame rate and cpu usage
	clock.tick(frame_rate)

	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.KEYDOWN:
			if pygame.key.get_mods() & command_key:
				if event.key == pygame.K_q:
					done = True

	# draw
	screen.fill(background_color)

	pygame.draw.line(screen, white, [center[0]-10, center[1]], [center[0]+10, center[1]], 1)
	pygame.draw.line(screen, white, [center[0], center[1]-10], [center[0], center[1]+10], 1)

	warning_string = "Warning!"
	warning_render = warning_font.render(warning_string, warning_aa, warning_color)
	warning_location = [center[0] - warning_render.get_width()/2, center[1] - warning_font.get_ascent()]
	screen.blit(warning_render, warning_location)

	pygame.display.flip()

# quit
pygame.quit()
