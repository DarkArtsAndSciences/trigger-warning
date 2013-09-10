import boids
import interface_manager
import state_manager
import time_manager
import trigger_manager

#import cProfile as profile

state_manager.init()
time_manager.init()
trigger_manager.init()
interface_manager.init()
boids.init()

interface_manager.loop()
#profile.run('interface_manager.loop()', sort='cumulative')
