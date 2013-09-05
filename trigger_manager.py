import utils

"""Warnings

A warning is a function that affects the game interface.

Most warnings will have a short title and a longer text description. A warning may also have a custom function with kwargs, which can be set in define_warning() and overridden in warn().
"""

warnings = {}
def define_warning(wid, title, text, func, **kwargs):
	warnings[wid] = (title, text, func, kwargs)

def warn(wid, **kwargs):
	title, text, func, default_kwargs = warnings[wid]

	# TODO: pass to queue in interface_manager to draw/fadeout in draw_state()
	print title
	print text

	if kwargs and not default_kwargs:
		func(**kwargs)
	elif default_kwargs and not kwargs:
		func(**default_kwargs)
	elif default_wargs and kwargs:
		combined_kwargs = default_kwargs.copy()
		combined_kwargs.update(kwargs)
		func(**combined_kwargs)
	else:
		func()

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

#def is_effective(eid, now):
#	return now >= effect_queue[eid][0]

def affect(eid):
	event, kwargs = effects[eid]
	event(**kwargs)

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
def define_trigger(tid, wid, eid, context=None):
	triggers[tid] = (wid, eid, context)

def fire(tid):
	wid, eid, context = triggers[tid]
	warn(wid)
	add_effect(eid, 10)  # TODO: since + 10s

def handle_triggers():
	for tid in triggers:
		# if context matches
		fire(tid)

"""Self Test"""

if __name__ == '__main__':

	def fade_warning(seconds):
		print 'Fade out warning text over {} seconds. Set a flag and let interface.draw_state() deal with it. Countdown the seconds by changing warning.text?'.format(seconds)
	define_warning('start warning', 'Warning', 'The game will start in ten seconds.', fade_warning, seconds=10)

	def start_effect():
		print 'start game'
	define_effect('start effect', start_effect)

	define_trigger('start trigger', 'start warning', 'start effect')

	print '-'*8
	handle_triggers()

	# TODO: handle_effects(11) to see start_effect()
