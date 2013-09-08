import math
import random

import pygame.draw

import settings
import state_manager
import time_manager

def init():
	settings.set('min boid size', 2)
	settings.set('max boid size', 5)
	settings.set('boid color', 'white')
	"""'number of boids' is set in trigger_manager.init"""

	state_manager.add_event_handler(add_boid, event_type='add boid')

"""
Flock
"""

flock = {}

def add_boid(name):
	flock[name] = Boid(name)

def add_boids(num_boids, current_context):
	#print 'adding {} boids'.format(num_boids)
	time_per_boid = 10.0 / num_boids
	for i in xrange(num_boids):
		state_manager.delay_event('add boid', time_manager.get_real_future_time(i*time_per_boid), name='boid {}'.format(i))

def draw_boids(surface):
	for boid in flock:
		flock[boid].draw(surface)

"""
Behavior
"""

behaviors = []

def add_rule(type, func, **kwargs):
	"""Add a behavior rule to the flock.

	type: 'self' or 'flock'
		self: func(boid) will be called once for each boid in the flock
		flock: func(boid, other) will be called once for every pair of boids in the flock. FLOCK RULES ARE SLOW FOR LARGE FLOCKS.

	func: a function that returns a Point which will affect its boid's velocity.

		It must accept the required parameters for its type as listed above. It may also have any kwargs except 'type' and the names in update_boid's local_kwargs.

		It may have side effects (i.e. to change emotions on collision), but be aware that directly affecting Boid.p or .v will look like the boid was moved by an outside force instead of flying there under its own power.

	average [optional, defaults to 1]: 'flock' rules only. 'flock size', 'near boids' or an int (typically, the number of boids affected by the rule). The points from each boid pair will be summed, then divided by this value.

	rule_type [required for flock rules, defaults to 'as-is']:
		Determines what to do with the point produced by summing and averaging the points from each pair of boids.
		as-is: nothing
		towards: vector from 'boid' to it
		velocity: ?

	scale [optional, defaults to 1]: Multiply the effect of this rule by this value.
	"""
	behaviors.append((type, func, kwargs))

def random_rule(boid):
	"""Rule random.random(): Boids move randomly"""
	return Point((random.random()-0.5), (random.random()-0.5))
add_rule('self', random_rule, scale=0.001)

def towards_center(boid, other):
	"""Rule 1: Boids fly towards the flock's center"""
	return other.p
add_rule('flock', towards_center, average='flock size', scale=0.01, rule_type='towards')

def avoid_collision(boid, other):
	"""Rule 2: Boids try to keep a min distance away from other boids"""
	if boid.p.distance(other.p) < boid.too_close:
		boid.collisions += 1  # anger

		"""Move towards smaller boids and away from larger boids.
		TODO: more behaviors for different moods
		"""
		if (boid.size == other.size):
			scale = -1
		else:
			scale = boid.size / (boid.size - other.size) - 1

		"""Return the distance between us * the towards/away multiplier."""
		return (other.p - boid.p) * scale
add_rule('flock', avoid_collision, rule_type='as-is')

def match_velocity(boid, other):
	"""Rule 3: Boids try to fly at the same speed as nearby boids"""
	distance = boid.p.distance(other.p)
	if distance < boid.near:  # if this boid is close to that boid
		return other.v * (boid.near - distance)/boid.near
add_rule('flock', match_velocity, average='near boids', rule_type='velocity')

def stay_on_screen(boid, border=0, speed=1):
	"""Rule: Boids try to stay on screen"""
	size = settings.get('size')
	if boid.p.x < border:
		x = (border - boid.p.x)*speed
	elif boid.p.x > size[0]-border:
		x = (size[0]-border - boid.p.x)*speed
	else:
		x = 0
	if boid.p.y < border:
		y = (border - boid.p.y)*speed
	elif boid.p.y > size[1]-border:
		y = (size[1]-border - boid.p.y)*speed
	else:
		y = 0
	return Point(x,y)
add_rule('self', stay_on_screen, border=100, speed=0.1)

def mouse_attract(boid, attractiveness):
	"""Rule: If the mouse is down, fly towards it"""
	if pygame.mouse.get_pressed()[0]:
		mouse_point = Point(*pygame.mouse.get_pos())
		return (mouse_point - boid.p) * attractiveness * mouse_point.speed()
add_rule('self', mouse_attract, attractiveness=0.0002)

# TODO: add perching / prevent boids going below the screen

def update_boids():
	"""Calculate a new velocity and position for each boid in the flock.

	This function should be called once per frame, before drawing the boids.

	With a large flock, most of the CPU time goes to this function. If the game is too slow with many boids, this is the function to optimize. (If the game is still too slow with three boids, it's something else.)
	"""
	flock_size = len(flock)-1
	local_kwargs = ['average', 'scale', 'rule_type']

	for boid in flock:
		flock[boid].update_mood()

		"""Flock rules"""
		v = [Point(0,0)]*len(behaviors)

		for other in flock:  # this is the slowest line in the entire codebase
			if flock[other] is boid: continue

			for i, (type, func, kwargs) in enumerate(behaviors):
				if type == 'flock':
					func_kwargs = {k:kwargs[k] for k in kwargs if k not in local_kwargs}
					vi = func(flock[boid], flock[other], **func_kwargs)
					if vi: v[i] += vi

		for i, (type, func, kwargs) in enumerate(behaviors):
			if type == 'self':
				func_kwargs = {k:kwargs[k] for k in kwargs if k not in local_kwargs}
				vi = func(flock[boid], **func_kwargs)
				if vi: v[i] += vi

			if 'average' in kwargs:
				if kwargs['average'] == 'flock size':
					average = flock_size
				elif kwargs['average'] == 'near boids':
					average = len(flock[boid].get_near_boids(flock[boid].near))
				if average == 0:
					average = 1
				v[i] /= average

			if 'scale' in kwargs:
				scale = kwargs['scale']
			else:
				scale = 1

			if 'rule_type' in kwargs:
				if kwargs['rule_type'] == 'towards':
					v[i] = (v[i] - flock[boid].p) * scale
				elif kwargs['rule_type'] == 'velocity':
					v[i] = (v[i] - flock[boid].v) * scale
				else:  # 'as-is' or unrecognized
					v[i] = v[i] * scale

		for vi in v:
			vi /= settings.get('frame rate')  # per second -> per frame
			flock[boid].v += vi  # update velocity

		"""Speed limit"""
		min_speed = flock[boid].size * 1.5
		max_speed = min_speed + (Boid.max_size - flock[boid].size)
		max_speed += flock[boid].collisions/20.0  # anger
		max_speed += v[-2].speed()  # don't limit mouse attraction
		max_speed += v[-1].speed()  # or keep-on-screen
		current_speed = flock[boid].v.speed()
		if current_speed > max_speed:
			flock[boid].v /= current_speed * max_speed
		if current_speed < min_speed:
			flock[boid].v *= min_speed - current_speed

		flock[boid].p += flock[boid].v  # update position

"""
Points
"""

class Point:
	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)
	def __str__(self):
		return "{},{}".format(round(self.x,3), round(self.y,3))
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
		# TODO: consider inlining this for speed
		return math.hypot(self.x - other.x, self.y - other.y)
	def velocity(self):
		# TODO: can this be sped up?
		return Point(0,0).distance(self)
	def speed(self):
		# TODO: can this be sped up?
		return math.fabs(self.velocity())

"""
Boids
"""

class Boid:
	min_size = 1
	max_size = 5

	def __init__(self, name):
		"""Physics"""
		screen_size = settings.get('size')
		x = random.randrange(screen_size[0])
		y = random.randrange(screen_size[1])
		self.p = Point(x,y)
		self.v = Point(0,0)
		#self.size = random.randrange(Boid.min_size, Boid.max_size)
		self.size = random.choice([1,1,1,1,1,2,2,2,3,4,5])
		self.near = self.size * screen_size[0]/15
		self.too_close = self.size * screen_size[0]/75

		"""Display"""
		self.name = name
		self.color = 'boid color'

		"""Mood"""
		self.triggered = False
		self.collisions = 0
		self.last_mood_change = 0

		"""Boids change their mood no more often than once per second, but some boids may wait up to five seconds longer."""
		self.mood_length = 1 + 5*random.random()

	def __str__(self):
		return "boid at {},{}".format(self.p.x, self.p.y)

	def __repr__(self):
		return "[Boid x={}, y={}]".format(self.p.x, self.p.y)

	def get_rect(self):
		return (self.p.x, self.p.y, self.size, self.size)

	def get_near_boids(self, distance=None):
		"""Return a list of all boids within distance."""
		if not distance: distance = self.near
		return [b for b in flock if self is not b and self.p.distance(flock[b].p)<=self.near]

	def draw(self, surface):
		color = settings.get_color(self.color)
		alpha = 255 #- self.collisions  # TODO: health, not mood

		"""TODO: Try replacing this with a subsurface for a speed boost."""
		fade_surface = pygame.surface.Surface((self.size, self.size))
		fade_surface.set_alpha(alpha)
		pygame.draw.rect(fade_surface, color, [0,0,self.size,self.size])
		surface.blit(fade_surface, self.get_rect())

	def update_mood(self):
		"""Update and display this boid's mood."""

		"""Boids wait mood_length seconds between mood changes. Time edits are ignored."""
		now = time_manager.get_real_since().total_seconds()
		if now < self.last_mood_change + self.mood_length: return
		self.last_mood_change = now

		"""Boids have short memories."""
		if self.collisions:  # forget half of them
			self.collisions /= 2

		"""Boids change color to display their mood to the flock and to the player."""
		if (self.collisions > len(flock)): self.color = 'blue'
		if (self.collisions > len(flock)*2): self.color = 'red'
		if (self.triggered): self.color = 'yellow'
