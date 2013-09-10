import itertools
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

flock = []

"""For fast access in update_boids, position and velocity are stored here instead of inside the Boid instances."""
flock_px = [] # (x,y) position
flock_py = []
flock_vx = [] # (x,y) velocity
flock_vy = []

def add_boid(name):
	boid = Boid()

def add_boids(num_boids, current_context):
	time_per_boid = 10.0 / num_boids
	for i in xrange(num_boids):
		state_manager.delay_event('add boid', time_manager.get_real_future_time(i*time_per_boid), name='boid {}'.format(i))

def draw_boids(surface):
	for boid in flock:
		boid.draw(surface)

"""
Behavior
"""

flock_rule = []
solo_rule = []

"""Add a behavior rule to the flock.

Flock rules: func(boid) will be called once for each boid in the flock
Solo rules: func(boid, other) will be called once for every pair of boids in the flock. FLOCK RULES ARE SLOW FOR LARGE FLOCKS.

func: a function that returns an (x,y) which will affect its boid's velocity.

	It must accept the required parameters for its type as listed above. It may also have any kwargs except 'type' and the names in update_boid's local_kwargs.

	It may have side effects (i.e. to change emotions on collision), but be aware that directly affecting Boid.p or .v will look like the boid was moved by an outside force instead of flying there under its own power.

average [optional, defaults to 1]: 'flock' rules only. 'flock size', 'near boids' or an int (typically, the number of boids affected by the rule). The points from each boid pair will be summed, then divided by this value.

rule_type [required for flock rules, defaults to None]:
	Determines what to do with the point produced by summing and averaging the points from each pair of boids.
	as-is: nothing
	towards: vector from 'boid' to it
	velocity: ?

scale [optional, defaults to 1]: Multiply the effect of this rule by this value.
"""
def add_flock_rule(func, rule_type=None, average=1, scale=1, **fargs):
	flock_rule.append((func, fargs, rule_type, average, scale))

def add_solo_rule(func, **fargs):
	solo_rule.append((func, fargs))

def random_rule(boid, scale):
	"""Rule random.random(): Boids move randomly"""
	return round((random.random()-0.5)*scale,2), round((random.random()-0.5)*scale,2)
add_solo_rule(random_rule, scale=0.001)

def towards_center(boid, other):
	"""Rule 1: Boids fly towards the flock's center"""
	#print 'towards_center({},{}) = {},{}'.format(boid, other, flock_px[other], flock_py[other])
	return flock_px[other], flock_py[other]
add_flock_rule(towards_center, 'towards', average='flock size', scale=0.01)

def avoid_collision(boid, other):
	"""Rule 2: Boids try to keep a min distance away from other boids"""
	if distance(boid, other) < flock[boid].too_close:
		flock[boid].collisions += 1  # anger

		"""Move towards smaller boids and away from larger boids.
		TODO: more behaviors for different moods
		"""
		bs = flock[boid].size
		os = flock[other].size
		if (bs == os):  # if the two boids are the same size
			scale = -1  # move away equally
		else:
			scale = bs/(bs-os) -1  # smooth falloff for other sizes

		"""Return the distance between us * the towards/away multiplier."""
		return (flock_px[other]-flock_px[boid])*scale, (flock_py[other]-flock_py[boid])*scale
	return 0,0
add_flock_rule(avoid_collision)

def match_speed(boid, other):
	"""Rule 3: Boids try to fly at the same speed as nearby boids"""
	d = distance(boid, other)
	near = flock[boid].near
	if d < near:  # if this boid is close to that boid
		m = (near - d)/near  # smooth falloff
		return flock_vx[other]*m, flock_vy[other]*m
	return 0,0
add_flock_rule(match_speed, 'velocity', 'near boids')

def stay_on_screen(boid, border=0, speed=1):
	"""Rule: Boids try to stay on screen"""
	size = settings.get('size')
	if flock_px[boid] < border:
		x = (border - flock_px[boid])*speed
	elif flock_px[boid] > size[0]-border:
		x = (size[0]-border - flock_px[boid])*speed
	else:
		x = 0
	if flock_py[boid] < border:
		y = (border - flock_py[boid])*speed
	elif flock_py[boid] > size[1]-border:
		y = (size[1]-border - flock_py[boid])*speed
	else:
		y = 0
	return x,y
add_solo_rule(stay_on_screen, border=100, speed=0.1)

def mouse_attract(boid, attractiveness):
	"""Rule: If the mouse is down, fly towards it"""
	if pygame.mouse.get_pressed()[0]:
		mousex, mousey = pygame.mouse.get_pos()
		x = mousex - flock_px[boid]
		y = mousey - flock_py[boid]
		m = attractiveness * speed(x,y)
		return x*m, y*m
	return 0,0
add_solo_rule(mouse_attract, attractiveness=0.000001)

# TODO: add perching / prevent boids going below the screen

def update_boids():
	"""Calculate a new velocity and position for each boid in the flock.

	This function should be called once per frame, before drawing the boids.

	With a large flock, most of the CPU time goes to this function. If the game is too slow with many boids, this is the function to optimize. (If the game is still too slow with three boids, it's something else.)
	"""
	flock_size = len(flock)
	if flock_size == 0: return

	for boid in xrange(flock_size):
		flock[boid].update_mood()

		"""Behavior rules"""
		sv = [(0,0)]*len(solo_rule)
		fv = [[(0,0)]*len(flock)]*len(flock_rule)

		for rule, (func, fargs, _,_,_) in enumerate(flock_rule):
			fv[rule] = [func(boid,other,**fargs) for other in xrange(flock_size) if other != boid]

		for rule, (func, fargs) in enumerate(solo_rule):
			sv[rule] = func(boid, **fargs)

		for rule, (func, fargs, rule_type, average, scale) in enumerate(flock_rule):

			"""Sum the list of points into a single point."""
			fv[rule] = map(sum,itertools.izip(*fv[rule]))
			if not fv[rule] or not fv[rule][0] or not fv[rule][1]: continue

			if average == 'flock size':
				average = flock_size-1
			elif average == 'near boids':
				average = len(flock[boid].get_near_boids())
			if average == 0: average = 1  # avoid /0 errors
			if average != 1:
				fv[rule] = (fv[rule][0]/average, fv[rule][1]/average)

			if rule_type == 'towards':
				fv[rule] = ((fv[rule][0]-flock_px[boid])*scale, (fv[rule][1]-flock_py[boid])*scale)
			elif rule_type == 'velocity':
				fv[rule] = ((fv[rule][0]-flock_vx[boid])*scale, (fv[rule][1]-flock_vy[boid])*scale)
			else:
				fv[rule] = (fv[rule][0]*scale, fv[rule][1]*scale)

		"""Combine all the rules into one point."""
		mouse_v = sv[-1]
		onscreen_v = sv[-2]

		#sv = map(sum,itertools.izip(*sv)) or (0,0)
		sv = sv[0]
		fv = map(sum,itertools.izip(*fv)) or (0,0)
		fr = settings.get('frame rate')  # per second -> per frame
		v = ((sv[0]+fv[0])*fr, (sv[1]+fv[1])*fr)

		"""Speed limit"""
		min_speed = int(flock[boid].size * 1.5)
		max_speed = min_speed + (Boid.max_size - flock[boid].size)
		max_speed += flock[boid].collisions/20.0  # anger
		current_speed = speed(*v)
		if current_speed > max_speed:
			m = current_speed * max_speed
			v = (v[0]/m, v[1]/m)
		if current_speed < min_speed:
			m = min_speed - current_speed
			v = (v[0]*m, v[1]*m)

		v = (v[0]+mouse_v[0]+onscreen_v[0], v[1]+mouse_v[1]+onscreen_v[1])

		"""Update the boid's velocity."""
		flock[boid].update_velocity(*v)

"""
Points
"""

def distance(boid, other):
	return math.sqrt((flock_px[boid]-flock_px[other])**2 + (flock_py[boid]-flock_py[other])**2)

def speed(x, y):
	return math.sqrt(x**2 + y**2)

"""
Boids
"""

class Boid:
	min_size = 1
	max_size = 5

	def __init__(self):
		"""Flock id"""
		self.id = len(flock)
		flock.append(self)

		"""Physics"""
		screen_size = settings.get('size')
		flock_px.append(random.randrange(screen_size[0]))
		flock_py.append(random.randrange(screen_size[1]))
		flock_vx.append(0)
		flock_vy.append(0)

		#self.size = random.randrange(Boid.min_size, Boid.max_size)
		self.size = random.choice([1,1,1,1,1,2,2,2,3,4,5])

		self.near = self.size * screen_size[0]/15
		self.too_close = self.size * screen_size[0]/75

		"""Display"""
		self.color = 'boid color'

		"""Mood"""
		self.triggered = False
		self.collisions = 0
		self.last_mood_change = 0

		"""Boids change their mood no more often than once per second, but some boids may wait up to five seconds longer."""
		self.mood_length = 1 + 5*random.random()

	def __str__(self):
		return "boid #{} size {} at {},{} speed {},{}".format(self.id, self.size,  round(self.px,2),round(self.py,2), round(self.vx,2), round(self.vy,2))

	def __repr__(self):
		return "Boid(id={}, size={}, px={}, py={}, vx={}, vy={}, color={})".format(self.id, self.size, self.px, self.py, self.vx, self.vy, self.color)

	@property
	def px(self): return flock_px[self.id]
	@property
	def py(self): return flock_py[self.id]
	@property
	def vx(self): return flock_vx[self.id]
	@property
	def vy(self): return flock_vy[self.id]
	@vx.setter
	def vx(self, value): flock_vx[self.id] = value
	@vy.setter
	def vy(self, value): flock_vy[self.id] = value

	@property
	def rect(self):
		return (flock_px[self.id], flock_py[self.id], self.size, self.size)

	def get_near_boids(self, within=None):
		"""Return a list of all boids within distance."""
		if not within: within = self.near
		return [b for b in flock if self is not b and distance(self.id,b.id)<=within]

	def update_velocity(self, x, y):
		flock_vx[self.id] += x
		flock_vy[self.id] += y
		flock_px[self.id] += flock_vx[self.id]
		flock_py[self.id] += flock_vy[self.id]

	def draw(self, surface):
		color = settings.get_color(self.color)
		alpha = 255 #- self.collisions  # TODO: health, not mood

		"""TODO: Try replacing this with a subsurface for a speed boost."""
		fade_surface = pygame.surface.Surface((self.size, self.size))
		fade_surface.set_alpha(alpha)
		pygame.draw.rect(fade_surface, color, [0,0,self.size,self.size])
		surface.blit(fade_surface, self.rect)

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
