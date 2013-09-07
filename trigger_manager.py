import boids
import settings
import state_manager
import time_manager
import utils

def init():
	settings.set('collision trigger size', 20)
	settings.set('number of boids', 10)

	define_warning('start warning', 'Warning', 'The game will start in ten seconds.\n\nYou have been warned.', boids.add_boids, num_boids=settings.get('number of boids'))

	def start_effect(**kwargs):
		print 'start effect'
		# TODO: level 1's triggers go live here
	define_effect('start effect', start_effect)

	def test_warning(**kwargs):
		settings.set('foreground color', 'yellow')
	define_warning('test warning', 'Test Warning', 'This is only a test.', test_warning)

	def test_effect(**kwargs):
		settings.set('foreground color', 'green')
	define_effect('test effect', test_effect)

def start(current_context):
	define_trigger('start trigger', 'start warning', 'start effect', {'when':current_context['now']})

	define_trigger('test trigger', 'test warning', 'test effect', {'when':time_manager.plus(current_context['now'], 10), 'repeat':3, 'delay':15})

def tick(current_context):
	handle_triggers(current_context)
	handle_effects(current_context)

"""Warnings

A warning is a function that affects the game interface.

Most warnings will have a short title and a longer text description. A warning may also have a custom function with kwargs, which can be set in define_warning() and overridden in warn().
"""

warnings = {}
def define_warning(wid, title, text, func, **kwargs):
	warnings[wid] = (title, text, func, kwargs)

warning_queue = []
def warn(wid, current_context, **kwargs):
	title, text, func, default_kwargs = warnings[wid]

	warning_queue.append((title, text, current_context['since']))

	if not func: return

	if kwargs and not default_kwargs:
		func(current_context=current_context, **kwargs)
	elif default_kwargs and not kwargs:
		func(current_context=current_context, **default_kwargs)
	elif default_kwargs and kwargs:
		combined_kwargs = default_kwargs.copy()
		combined_kwargs.update(kwargs)
		func(current_context=current_context, **combined_kwargs)
	else:
		func(current_context=current_context)

"""Effects

An effect is a function that affects the game state or settings.

After the warning, the effect is placed in a queue until its time is up on the in-game clock. This time is always 10 seconds after the warning and cannot be edited. Other attributes of the effect can be edited while the effect is in the event queue (and an effect that affects the event queue itself is legal...)

When its time is up, the effect is called once (not per frame) and is not editable or removable once applied, even if time is rewound.
"""

effects = {}
def define_effect(eid, event, **kwargs):
	effects[eid] = (event, kwargs)

effect_queue = []
def add_effect(eid, when):
	effect_queue.append((eid, when))

def affect(eid, current_context):
	event, kwargs = effects[eid]
	event(current_context=current_context, **kwargs)

def handle_effects(current_context):
	for qid, (eid, when) in enumerate(effect_queue):
		if current_context['now'] >= when:
			affect(eid, current_context)
			del effect_queue[qid]  # queue item, not definition

"""Triggers

A trigger is a set of conditions and a warning/effect pair that will be created when those conditions are met.
"""

"""
Context
victim=None, who=None, what=None, when=None, where=None, why=None, how=None, **kwargs

add_effect('scared of mouse noise', who='mouse', what='avoid', why='noise')
add_effect('scared of unknown noise', who='unknown', what='avoid', when=20, where=(100,200), why='noise')

victim: which boid this trigger affects (None for all)
who: who/what caused this trigger (boid name, 'mouse', 'fate')
what: type of trigger ('avoid', 'attract')
when: when this trigger was set
	since-seconds, string for special cases
		'on state: {state}': on entering state (once)
		'in state: {state}': during state (every frame)
		'out state: {state}': on leaving state (once)
		'key: {key} {mods}': on keypress
		'mouse: {x,y} {distance}': on nearby mouse
		'click: {x,y} {distance}': on nearby click
where: x,y location
why: what caused this trigger ('noise', 'pain')
how: FUNCTION TO ADD TO THIS BOID'S PHYSICS
"""

triggers = {}
def define_trigger(tid, wid, eid, context):
	triggers[tid] = (wid, eid, context)

def is_same_context(context, current_context):
	"""Return true if current_context meets the conditions defined in context.

	The two contexts are both dicts, but have different keys. Be careful with the order of arguments: the first one is the ideal conditions (from the trigger) and the second is the actual conditions (from the game state).

	context:
		when:
			if int: time to go live; match if since >= when
			if string: special cases: 'inf', ..?

	current_context:
		from settings:
			?
		from interface_manager:
			?
		from state_manager:
			state
		from time_manager:
			now, real_now, since, real_since
			now+10: now + 10 seconds
				If the caller builds this, this module doesn't need to import datetime. Use total_seconds() to force a datetime back to seconds.
		from pygame:
			mouse location
			mouse up/down
			keys currently down
	"""

	"""Return true if time is up (now >= when)."""
	if 'when' in context and 'now' in current_context:
		if context['when'] <= current_context['now']:
			return True

	"""If nothing matched, return False."""
	return False

def handle_triggers(current_context):
	for tid in triggers.copy():
		wid, eid, context = triggers[tid]

		if is_same_context(context, current_context):
			warn(wid, current_context)
			add_effect(eid, current_context['now+10'])

			if not 'repeat' in context:
				del triggers[tid]

			else:
				if isinstance(context['repeat'], int):
					context['repeat'] -= 1
					if context['repeat'] <= 0:
						del triggers[tid]

				context['when'] = time_manager.plus(current_context['now'], context['delay'])  # Crash? You forgot to set a delay in define_trigger(context{HERE}). Don't just set it to zero unless you really want it to be called every frame.

"""Self Test
python trigger_manager.py
"""
if __name__ == '__main__':

	def fade_warning(**kwargs):
		print kwargs
		print "Fade out warning text over {seconds} seconds, ending at {current_context[now+10]}s. Set a flag and let interface.draw_state() deal with it. Countdown the seconds by changing warning.text?".format(**kwargs)
	define_warning('start warning', 'Warning', 'The game will start in ten seconds.', fade_warning, seconds=10)

	def start_effect(**kwargs):
		print 'start game'
	define_effect('start effect', start_effect)

	define_trigger('start trigger', 'start warning', 'start effect', {'when':2})

	handle_triggers({'now':2, 'now+10':12})
	handle_effects({'now':12, 'now+10':22})
