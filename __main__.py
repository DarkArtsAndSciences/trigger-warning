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

	'clock font': {'scale':4},
	'clock color': 'yellow',

	'fps font': {'scale':1},
	'fps color': 'yellow'
})
interface_manager.init()
time_manager.start()
interface_manager.start()
