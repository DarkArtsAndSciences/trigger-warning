import settings
import interface_manager
import state_manager
import time_manager
import trigger_manager
import utils

settings.init({
	'title': 'Trigger Warning',
	'credits': """www.darkartsandsciences.com""",

	'size': [800, 600],
	'trigger size': 20,

	'live trigger color': 'green',
	'dead trigger color': 'blue',
	'warning color': 'red',
	'chalk color': [255,250,205],
	'boid color': 'white',

	"""Fonts: Futura, Unispace, Chalkduster"""
	'default font': {'name':None, 'scale':1, 'aa':True, 'color':'foreground color'},
	'title font': {'name':'chalkduster', 'scale':3.5, 'color':'chalk color'},
	'intro font': {'name':'rabiohead', 'scale':2.5, 'color':'chalk color'},
	'clock font': {'name':'unispace', 'scale':2},
	'warning title font': {'name':'chalkduster', 'scale':3, 'color':'rotate: red, red, red, magenta, red, red, red, magenta, white, magenta'},
	'warning text font': {'name':'rabiohead', 'scale':2, 'color':'red'},
	'fps font': {'name':'futura', 'scale':0.85, 'color':'light gray'},
	'label font': {'name':'futura', 'scale':0.75}

})
time_manager.init()
trigger_manager.init()
interface_manager.init()

interface_manager.loop()
