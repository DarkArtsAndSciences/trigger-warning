import settings
import interface_manager
import state_manager
import time_manager
import utils

settings.init({
	'title': 'Trigger Warning',
	'credits': """www.darkartsandsciences.com""",

	'size': [800, 600],
	'trigger size': 20,

	'live trigger color': 'green',
	'dead trigger color': 'blue',
	'warning color': 'red',

	'default font': {'name':None, 'scale':1, 'aa':True, 'color':'foreground color'},
	'title font': {'name':'chalkduster', 'scale':4},
	'intro font': {'name':'chalkduster', 'scale':1.5},
	'clock font': {'name':'unispace', 'scale':2},
	'fps font': {'name':'futura', 'scale':0.75},
	'label font': {'name':'futura', 'scale':0.75}

})
interface_manager.init()
time_manager.start()
interface_manager.start()
