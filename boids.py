import random
import pygame.draw
import settings

boids = {}

def add_boid(name, x, y, size, color='boid color'):
	#boids[name] = (x, y, size, color)
	boids[name] = Boid(x, y, size, color)

def add_boids(num_boids, current_context):
	for i in xrange(num_boids):
		name = 'boid {}'.format(i)
		screen_size = settings.get('size')
		x = random.randrange(screen_size[0])
		y = random.randrange(screen_size[1])
		size = random.randrange(1,4)
		add_boid(name, x, y, size)

def draw_boids(surface):
	for name in boids:
		color = settings.get_color(boids[name].color)
		pos = [int(boids[name].p.x), int(boids[name].p.y)]
		size = boids[name].size
		pygame.draw.circle(surface, color, pos, size)

def update_boids():
	for name in boids:
		boids[name].update()

"""Physics"""

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

class Boid:
	max_size = 5

	def __init__(self, x, y, size, color):
		# physics
		self.p = Point(x, y)
		self.v = zero_point
		self.size = size

		# display
		self.color = color

		# mood
		self.triggered = False
		self.collisions = 0
		self.last_mood_change = 0

		# boids change their mood no more often than once per second,
		# but some boids may wait up to five seconds longer
		self.mood_length = 1 + 5*random.random()

		#boids.append(self)

	def __str__(self):
		return "boid at {},{}".format(self.p.x, self.p.y)

	def __repr__(self):
		return "[Boid x={}, y={}]".format(self.p.x, self.p.y)

	def get_rect(self):
		return (self.p.x, self.p.y, self.size, self.size)

	#def draw(self, screen, fade=1):
	#	surface = pygame.surface.Surface((self.size, self.size))
	#	surface.set_alpha(255*fade)
	#	pygame.draw.rect(surface, settings.get_color(self.color), surface.get_rect())
	#	screen.blit(surface, self.get_rect())

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
		def towards_location(p, scale=1):
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
		if (self.collisions > 10): self.color = 'blue'
		if (self.collisions > 20): self.color = 'red'
		if (self.triggered): self.color = 'yellow'
