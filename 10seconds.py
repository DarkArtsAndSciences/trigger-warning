"""
Ludum Dare 27: 10 Seconds
Trigger Warning
   by
Dark Arts and Sciences

Boids pseudocode from [http://www.kfish.org/boids/pseudocode.html], ported during the competition.

Requires python and pygame.

Controls:
	Hold down the mouse to attract boids.
	Boids set off triggers that they touch.
	Boids are yellow if they have touched a trigger, blue if they're angry about other boids flying too close, and red if they're very angry.

Luckily for you, I ran out of time.
Turning boids yellow is the ONLY thing triggers do.
I did not implement any painful triggers. (You're welcome.)

For future pain-enhanced versions, visit:
	darkartsandsciences.com

***

The last bug I couldn't fix before the Ludum Dare deadline looks like a one-line problem. Let's see how long it takes me to actually fix it.

Goal: when boids turn yellow, they also rewind the timer by one second.

Result: Yes, all I had to do was declare the variable as global. Four minutes including testing.

New feature: Trigger a boid, time rewinds by a second. Trigger enough boids at once, and you end up back in the intro.
"""

import math
import platform
import random
import time

class Trigger:
	def __init__(self, x, y, start, end=None, live=True):
		self.x = x
		self.y = y
		self.start = start
		self.end = end or float('inf')
		self.live = live
		self.triggered = False
		#print "created {}".format(self)

	def __str__(self):
		return "trigger at {},{} {}-{}".format(self.x, self.y, self.start, self.end)

	def get_rect(self):
		return (self.x, self.y, trigger_size, trigger_size)

class Warning:
	def __init__(self, string, trigger):
		self.string = string
		self.start = trigger.start
		self.end = trigger.start + 10
		#print "created {}".format(self)

	def __str__(self):
		return "warning {} at {}-{}".format(self.string, self.start, self.end)

	def draw(self, screen, fade=1):
		render = warning_font.render(self.string, warning_aa, warning_color)
		location = [center[0] - render.get_width()/2, center[1] - warning_font.get_ascent()]
		surface = pygame.surface.Surface((render.get_width(), render.get_height()))
		surface.set_alpha(255*fade)
		surface.blit(render, (0,0))
		screen.blit(surface, location)

class Effect:
	def __init__(self, effect, trigger, live=False):
		self.effect = effect
		self.trigger = trigger
		self.start = trigger.start + 10
		self.end = trigger.end + 10
		self.live = live
		#print "created {}".format(self)

	def __str__(self):
		return "effect at {}-{}: {}".format(self.start, self.end, self.effect)

import pygame
pygame.init()

# colors
black = [  0,  0,  0]
gray  = [127,127,127]
white = [255,255,255]
blue  = [  0,127,255]
green = [  0,255,  0]
red   = [255,  0,  0]
yellow = [255, 255, 0]

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
live_trigger_color = green
dead_trigger_color = blue
trigger_size = size[0]/40

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
text_pause = " "*10
intro_time = 20  # TODO: 10 for test, 20-30 for release
intro_fade_time = 2
intro_strings = ["These are Triggers."+text_pause*5,
	"A Trigger has a Warning and an Effect."+text_pause,
	"The Effect happens ten seconds after the Warning."+text_pause,
	"This time can not be changed."+text_pause*5,
	"Time itself can be changed."]
intro_length = sum([len(s) for s in intro_strings])
letters_per_second = intro_length/intro_time
intro_pauses = [(0.95, 0.985), (1.0, 1.1)]
intro_pauses = [(x*intro_time, y*intro_time) for x,y in intro_pauses]
line_spacing = 2.5
intro_offset = 100

# boids
class Point:
	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)
	def __str__(self):
		return "{},{}".format(self.x, self.y)
	def __repr__(self):
		return "Point({},{})".format(self.x, self.y)
	def __add__(self, other):
		return Point(self.x + other.x, self.y + other.y)
	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other.y)
	def __mul__(self, multiplier):
		multiplier = float(multiplier)
		return Point(self.x * multiplier, self.y * multiplier)
	def __div__(self, divisor):
		divisor = float(divisor)
		return Point(self.x / divisor, self.y / divisor)
	def __abs__(self):
		return Point(abs(self.x), abs(self.y))
	def distance(self, other):
		d = other - self
		return math.hypot(d.x, d.y)
	def velocity(self):
		return Point(0,0).distance(self)
	def speed(self):
		return math.fabs(self.velocity())
zero_point = Point(0,0)
center_point = Point(center[0], center[1])

boids = []
class Boid:
	max_size = 5

	def __init__(self):
		# physics
		self.p = Point(random.randrange(size[0]), random.randrange(size[1]))
		self.v = zero_point
		self.size = random.randrange(1, Boid.max_size)

		# display
		self.color = white

		# mood
		self.triggered = False
		self.collisions = 0
		self.last_mood_change = 0

		# boids change their mood no more often than once per second,
		# but some boids may wait up to five seconds longer
		self.mood_length = 1 + 5*random.random()

		boids.append(self)

	def __str__(self):
		return "boid at {},{}".format(self.p.x, self.p.y)

	def __repr__(self):
		return "[Boid x={}, y={}]".format(self.p.x, self.p.y)

	def get_rect(self):
		return (self.p.x, self.p.y, self.size, self.size)

	def draw(self, screen, fade=1):
		surface = pygame.surface.Surface((self.size, self.size))
		surface.set_alpha(255*fade)
		pygame.draw.rect(surface, self.color, surface.get_rect())
		screen.blit(surface, self.get_rect())

	# update this boids position
	# v: new velocity
	# b: other boid
	def update(self):

		# given how to react to one other boid, calculate the outer loop
		# flock rules may have side effects for moods; don't touch the physics
		#
		# to return the flock's average, pass flocksize-1 to average
		# to scale the result, pass a multiplier to scale
		# type 'as-is' returns the resulting point
		# type 'towards' returns a vector from self.p to the point
		def flock_rule(per_boid=None, average=1.0, scale=1.0, type='as-is'):
			v = zero_point
			for other_boid in boids:
				if other_boid is self: continue
				if per_boid: v += (per_boid(other_boid) or zero_point)
			v /= average
			#print "flock rule: returning {}/{}*{} {}".format(v, average, scale, type)
			if type == 'as-is': return v * scale
			if type == 'towards': return(v - self.p) * scale
			if type == 'velocity': return(v - self.v) * scale

		# Rule random.random(): Boids move randomly
		def random_rule(scale=1.0):
			return Point((random.random()-0.5)*scale, (random.random()-0.5)*scale)
		v = random_rule(0.001)

		# Rule 1: Boids fly towards the flock's center
		v += flock_rule(per_boid=lambda b: b.p, average=len(boids)-1, scale=1.0/100, type='towards')

		# Rule 2: Boids keep a min distance away from other boids
		collision_distance = self.size * 2
		def avoid_collision(b):
			# if this boid is too close to that boid
			if self.p.distance(b.p) < collision_distance:
				# count near misses and get angry
				self.collisions += 1
				# move towards smaller birds and away from larger birds
				distance = b.p - self.p
				if (self.size == b.size):
					scale = -1
				else:
					scale = self.size / (self.size - b.size) - 1
				#print "near miss with boid sizes {}/{}, moving {}".format(self.size, b.size, distance*scale)
				return distance*scale
		v += flock_rule(avoid_collision)

		# Rule 3: Boids try to fly as fast as nearby boids
		match_velocity_distance = self.size * 50
		def match_velocity(b):
			# if this boid is close to that boid
			distance = self.p.distance(b.p)
			if distance < match_velocity_distance:
				return b.v * (match_velocity_distance - distance)/match_velocity_distance
		near_boids = len([b for b in boids if self.p.distance(b.p) < match_velocity_distance])
		v += flock_rule(match_velocity, average=near_boids, type='velocity')

		# Rule: Boids try to stay on screen
		def stay_on_screen(border=0, speed=1):
			if self.p.x < border:
				x = (border - self.p.x)*speed
			elif self.p.x > size[0]-border:
				x = (size[0]-border - self.p.x)*speed
			else:
				x = 0
			if self.p.y < border:
				y = (border - self.p.y)*speed
			elif self.p.y > size[1]-border:
				y = (size[1]-border - self.p.y)*speed
			else:
				y = 0
			return Point(x,y)
		on_screen = stay_on_screen(100,0.1)
		v += on_screen

		# Rule: Boids fly towards or away from locations
		def towards_location(p=center_point, scale=1):
			return (p - self.p) * scale

		# if the mouse is down, move towards it
		mouse_attract = 0.00005
		mouse_attracted = zero_point
		if pygame.mouse.get_pressed()[0]:
			mouse_point = Point(*pygame.mouse.get_pos())
			mouse_attracted = towards_location(mouse_point, mouse_attract*mouse_point.speed())
			v += mouse_attracted

		# convert from per second to per frame
		v /= frame_rate

		# update velocity
		self.v += v

		# speed limit
		min_speed = self.size * 1.5
		max_speed = min_speed + (1*Boid.max_size-self.size)
		max_speed += self.collisions/20.0  # anger
		max_speed += mouse_attracted.speed()  # don't limit mouse attraction
		max_speed += on_screen.speed()  # or keep-on-screen
		current_speed = self.v.speed()
		if current_speed > max_speed:
			self.v /= current_speed * max_speed
		if current_speed < min_speed:
			self.v *= min_speed - current_speed

		# update position
		self.p += self.v

	def change_mood(self, now_raw):
		# boids have short memories
		if now_raw < boid.last_mood_change + boid.mood_length: return
		boid.last_mood_change = now_raw

		# forget collisions
		if self.collisions: self.collisions /= 2

		# update color
		if (self.collisions > 10): self.color = blue
		if (self.collisions > 20): self.color = red
		if (self.triggered): self.color = yellow

def generate_boids(number=20):
	for n in range(number): Boid()

# triggers, warnings, and effects
trigger_y = intro_offset + intro_font.get_linesize() * (1+(line_spacing-1)/2) - trigger_size/2
triggers = [Trigger(None, None, intro_time + intro_fade_time + 1),  # start game
			Trigger(size[0]/4,   trigger_y, 1, float('inf'), False),  # left demo
			Trigger(size[0]*3/4, trigger_y, 1, float('inf'), False)]  # right demo
def enable_triggers():
	for trigger in triggers:
		trigger.live = True

warnings = [Warning("Warning!", triggers[0])]  # start game

def rewind_time():
	global offset
	offset -= 1

effects = [Effect(generate_boids, triggers[0]),
		   Effect(enable_triggers, triggers[0]),
		   Effect(rewind_time, triggers[1]),
		   Effect(rewind_time, triggers[2])]

# loop until quit
done = False
paused = False
reset = False
start = time.time()
clock = pygame.time.Clock()
offset = 0
while done == False:

	# limit frame rate and cpu usage
	clock.tick(frame_rate)

	# game time
	if paused: offset -= 1.0/frame_rate
	now_raw = time.time()
	now = now_raw + offset
	since_raw = now_raw - start
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
				if event.key == pygame.K_p:  # pause
					paused = True
				if event.key == pygame.K_r:  # rewind
					offset -= 0.25

		if event.type == pygame.KEYUP:
			if pygame.key.get_mods() & command_key:
				pass
			else:
				if event.key == pygame.K_p:  # unpause
					paused = False

	# draw

	# alpha multiplier, 0.0 < fade < 1.0
	def fade(show_since, fade_since=None, fade_length=10):
		if not fade_since: fade_since = show_since
		if since < show_since: return 0
		if since < fade_since: return 1
		if since > fade_since + fade_length: return 0
		return 1 - (since-fade_since)/fade_length

	# background
	screen.fill(background_color)

	# intro
	if (since < intro_time + intro_fade_time):
		for pause_start, pause_end in intro_pauses:
			if not paused and pause_start < since_raw < pause_end:
				paused = True
				reset = True
			if paused and reset and since_raw > pause_end:
				paused = False
				reset = False

		letters = int(since * letters_per_second)
		i = 0
		used = 0
		while (i < len(intro_strings) and used + len(intro_strings[i]) < letters):
			try: used += len(intro_strings[i])
			except IndexError: break
			i += 1
		intro_surface = pygame.surface.Surface((size[0], size[1]))
		intro_surface.set_alpha(255*fade(0, intro_time, intro_fade_time))
		j = 0
		try: strings = intro_strings[:i] + [intro_strings[i][:letters-used]]
		except IndexError: strings = intro_strings
		for string in strings:
			string_render = intro_font.render(string, intro_aa, intro_color)
			string_location = [intro_offset, intro_offset + j*intro_font.get_linesize()*line_spacing]
			intro_surface.blit(string_render, string_location)
			j += 1
		screen.blit(intro_surface, (0,0))

	# triggers
	for trigger in [t for t in triggers if t.start < since < t.end and t.x and t.y]:
		if trigger.live:
			trigger_color = live_trigger_color
			for b in boids:
				t_rect = pygame.Rect(trigger.get_rect())
				b_rect = pygame.Rect(b.get_rect())
				if t_rect.colliderect(b_rect):
					#print "{} hit {}".format(boid, trigger)
					trigger.triggered = True
					b.triggered = True
					for effect in effects:
						if effect.trigger is trigger:
							effect.effect()
		else:
			trigger_color = dead_trigger_color
		pygame.draw.ellipse(screen, trigger_color, trigger.get_rect())

	# boids
	for boid in boids:
		boid.change_mood(now_raw)
		boid.update()
		boid.draw(screen)

	# warnings
	for warning in warnings:
		wf = fade(warning.start)
		if 0 < wf <= 1: warning.draw(screen, wf)

	# effects
	for effect in effects:
		if (not effect.live) and (effect.start < since < effect.end):
			effect.live = True
			effect.effect()

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

	pygame.display.flip()

# quit
pygame.quit()
