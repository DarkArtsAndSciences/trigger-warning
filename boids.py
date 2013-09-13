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

limit: apply speed limit to this rule

scale [optional, defaults to 1]: Multiply the effect of this rule by this value.
"""
def add_flock_rule(func, rule_type=None, average=1, scale=1, limit=True, **fargs):
	flock_rule.append((func, fargs, rule_type, average, scale, limit))

def add_solo_rule(func, limit=False, **fargs):
	solo_rule.append((func, fargs, limit))

# TODO: move add_rule calls below into init()

def random_rule(boid, scale):
	"""Rule random.random(): Boids move in a random direction, like fireflies."""
	angle = random.random() * 2*math.pi
	scale *= random.random()
	x = math.cos(angle) * scale
	y = math.sin(angle) * scale
	return x,y

add_solo_rule(random_rule, scale=0.25, limit=True)

def towards_attract_point(boid, scale):
	"""Rule 1: Boids fly towards a point, usually the flock's center.

	Instead of having each boid recalculate the center of the rest of the flock, as in the original pseudocode, this function assumes that the center of the entire flock is in the global variable flock_center (set by update_boids once per frame) and simply subtracts this boid's contribution to the average.

	If the mouse is down, ignore the flock and use the mouse location as the attract point.

	If this boid is angry (blue), ignore the attract point. If this boid is very angry (red), fly AWAY from the attract point.

	TODO:
		Effects may change the attract point.
		Force flock_center to be within the screen boundaries.
		Boids should slow down before reaching their destination and avoid overshooting.
	"""

	"""Select the attract point."""
	if pygame.mouse.get_pressed()[0]:
		ax, ay = pygame.mouse.get_pos()

	elif flock_center:
		ax = flock_center[0] - flock_px[boid]/flock_size
		ay = flock_center[1] - flock_py[boid]/flock_size

	else:  # screen center
		screen_size = settings.get('size')
		ax, ay = screen_size[0]/2, screen_size[1]/2

	"""Select a behavior based on this boid's mood/color."""
	color = settings.get_color(flock[boid].color)
	angry = settings.get_color('blue')
	angrier = settings.get_color('red')

	if color == angry:  # ignore the attract point
		ax, ay = 0,0

	if color == angrier:  # move away instead of towards
		ax = -ax
		ay = -ay

	"""Calculate and return the movement vector."""
	x = ax - flock_px[boid]
	y = ay - flock_py[boid]
	m = scale #* speed(x,y)
	return x*m, y*m

add_solo_rule(towards_attract_point, scale=0.005, limit=False)

def avoid_collision(boid, other):
	"""Rule 2: Boids try to keep a min distance away from other boids."""

	d = distance(boid, other)
	btc = flock[boid].too_close
	otc = flock[other].too_close

	"""Check if the other boid is close enough to be a threat.
	Check d against btc to allow small boids to get inside bigger boids' personal space.
	Check d against btc+otc for a bubble-shield effect.
	"""
	if d > btc:
		return 0,0  # too far, ignore it

	"""Count collisions
	TODO: these are near misses; also count collisions, split anger and fear.
	NOTE: color won't change until update_mood() is called next frame
	"""
	flock[boid].collisions += 1  # anger

	"""Cache boid variables for speed and shorten names for readability."""
	bs = flock[boid].size
	os = flock[other].size

	"""Calculate the distance between boid and other."""
	bx = flock_px[boid]
	by = flock_py[boid]
	ox = flock_px[other]
	oy = flock_py[other]
	dx = ox - bx
	dy = oy - by

	"""Calculate the angle between boid and other."""
	ba = angle_between(flock_vx[boid], flock_vy[boid], True)
	oa = angle_between(flock_vx[other], flock_vy[other], True)
	da = math.fabs(ba - oa) # difference between boid directions
	ca = angle_between(flock_vx[other]-flock_vx[boid], flock_vy[other]-flock_vy[boid], True)

	'''
	TODO: Head-on and rear-end collisions result in high-speed reverse bounces, when they could avoid each other by flying sideways slightly. Fix, if it doesn't involve much CPU time (remember, this is a flock rule).
	if ca%180 < 45:
		print '  front collision'
		# move perpendicular to ca
	else:
		print '  side collision'
		# don't change motion?
	'''

	scale = -1  # default behavior (avoid): return -dx,-dy

	color = settings.get_color(flock[boid].color)
	angry = settings.get_color('blue')
	angrier = settings.get_color('red')

	if color == angry:  # attack smaller boids, flee larger
		if bs != os:  # prevent /0 error
			scale = bs/(bs-os) -1

	if color == angrier:  # very angry, attack everything!
		scale = bs

	return dx*scale, dy*scale

add_flock_rule(avoid_collision, limit=False)

def match_speed(boid, other):
	"""Rule 3: Boids try to fly at the same speed as nearby boids."""

	d = distance(boid, other)
	near = flock[boid].near
	if d < near:  # if this boid is close to that boid
		m = (near - d)/near  # smooth falloff for how close
		return flock_vx[other]*m, flock_vy[other]*m  # match their speed

	return 0,0

add_flock_rule(match_speed, 'velocity', 'near boids', scale=0.125, limit=True)

def stay_on_screen(boid, border=0, speed=1):
	"""Rule: Boids try to stay on screen.

	TODO: base border size on boid size
	"""

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

add_solo_rule(stay_on_screen, border=25, speed=0.05, limit=True)

"""TODO: Add rule for perching / prevent boids going below the screen."""

def update_boids():
	"""Calculate a new velocity and position for each boid in the flock.

	This function should be called once per frame, before drawing the boids.

	With a large flock, most of the CPU time goes to this function. If the game is too slow with many boids, this is the function to optimize. (If the game is still too slow with three boids, it's something else.)
	"""

	global flock_size
	flock_size = len(flock)
	if flock_size == 0: return

	"""Calculate the center of the entire flock."""
	global flock_center
	flock_center = [(flock_px[b],flock_py[b]) for b in xrange(flock_size)]
	flock_center = sum_points(flock_center)
	flock_center = flock_center[0]/flock_size, flock_center[1]/flock_size

	for boid in xrange(flock_size):

		"""Update this boid's mood with last frame's changes."""
		flock[boid].update_mood()

		"""Apply each solo rule to this boid."""
		sv = [func(boid,**fargs) for func,fargs,_ in solo_rule]

		"""Apply each flock rule to each boid/other pair and sum the results."""
		fv = [sum_points([func(boid,other,**fargs) for other in xrange(flock_size) if other!=boid]) for func,fargs,_,_,_,_ in flock_rule]

		"""For each flock rule, divide the sum by the number of boids involved.
		For 'towards' and 'velocity' rule types, subtract this boid's position or velocity, respectively.
		Multiply each point by its rule's scale.
		"""
		for rule, (func, fargs, rule_type, average, scale, _) in enumerate(flock_rule):

			if average == 'flock size':
				average = flock_size-1
			elif average == 'near boids':
				average = len(flock[boid].get_near_boids())
			if average == 0: average = 1  # avoid /0 errors
			fv[rule] = (fv[rule][0]/average, fv[rule][1]/average)

			if rule_type == 'towards':
				fv[rule] = ((fv[rule][0]-flock_px[boid])*scale, (fv[rule][1]-flock_py[boid])*scale)  # (v-b.p)*scale
			elif rule_type == 'velocity':
				fv[rule] = ((fv[rule][0]-flock_vx[boid])*scale, (fv[rule][1]-flock_vy[boid])*scale)  # (v-b.v)*scale
			else:
				fv[rule] = (fv[rule][0]*scale, fv[rule][1]*scale)

		"""Sum the points from rules where limit is True. limit is at index 2 for solo rules and 5 for flock rules."""
		lsv = sum_points([sv[i] for i in xrange(len(sv)) if solo_rule[i][2]])
		lfv = sum_points([fv[i] for i in xrange(len(fv)) if flock_rule[i][5]])
		lv = sum_points([lsv, lfv])
		current_speed = speed(*lv)

		"""Larger boids have a slower top speed."""
		#max_speed = min_speed + (Boid.max_size - flock[boid].size)
		max_speed = 7 - flock[boid].size

		"""Angrier boids have a faster top speed."""
		#max_speed += flock[boid].collisions/20.0  # anger

		"""If this boid is going too fast, slow it down."""
		if current_speed > max_speed:
			m = current_speed * max_speed
			lv = (lv[0]/m, lv[1]/m)

		"""Combine with the points from the rest of the rules."""
		usv = sum_points([sv[i] for i in xrange(len(sv)) if not solo_rule[i][2]])  # rules with limit=True
		ufv = sum_points([fv[i] for i in xrange(len(fv)) if not flock_rule[i][5]])
		v = sum_points([lv, usv, ufv])

		"""TODO: Moving boids have a minimum speed."""
		#current_speed = speed(*v)
		#if current_speed > 0:
		#	#min_speed = int(flock[boid].size * 1.5)
		#	min_speed = 1
		#	if current_speed < min_speed:
		#		m = current_speed * min_speed
		#		v = (v[0]/m, v[1]/m)

		"""Update the boid's velocity."""
		fr = settings.get('frame rate')  # per second -> per frame
		v = (v[0]/fr, v[1]/fr)
		flock[boid].update_velocity(*v)

"""
Points
"""

def distance(boid, other):
	return math.sqrt((flock_px[boid]-flock_px[other])**2 + (flock_py[boid]-flock_py[other])**2)

def speed(x, y):
	return math.sqrt(x**2 + y**2)

def angle_between(dx, dy, degrees=False):
	angle = math.atan2(-dy, dx)
	angle %= 2 * math.pi
	if degrees: angle = math.degrees(angle)
	return angle

def sum_points(points):
	"""Given a list of x,y tuples, return x1+x2+...,y1+y2..."""
	if not points: return 0,0
	if len(points) == 1: return points[0]
	return map(sum,itertools.izip(*points))

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
		self.size = random.choice([1,1,2,3,4,5])

		self.near = self.size * 10
		self.too_close = self.size * 5

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
	#@vx.setter
	#def vx(self, value): flock_vx[self.id] = value
	#@vy.setter
	#def vy(self, value): flock_vy[self.id] = value

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
		n = self.near
		tc = self.too_close
		s = self.size
		id = self.id

		csize = n*2, n*2
		ccent = n, n
		container = pygame.surface.Surface(csize, pygame.SRCALPHA)
		# TODO: blend modes?

		#alpha = 255 - self.collisions  # TODO: health, not mood
		#container.set_alpha(alpha)

		eye_color = settings.get_color('white', 248)
		boid_color = settings.get_color(self.color, 127)
		ring_color = settings.get_color(self.color, 15)

		pygame.draw.circle(container, ring_color, ccent, n, 1)
		pygame.draw.circle(container, ring_color, ccent, tc)
		pygame.draw.circle(container, ring_color, ccent, s*3, 2)
		pygame.draw.circle(container, boid_color, ccent, s*2, 1)
		pygame.draw.circle(container, eye_color, ccent, s)
		# TODO: draw head/tail line showing velocity angle/magnitude

		x = flock_px[id]
		y = flock_py[id]
		rect = (x - ccent[0], y - ccent[1], csize[0], csize[1])
		surface.blit(container, rect)

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
