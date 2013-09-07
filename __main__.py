import boids
import interface_manager
import state_manager
import time_manager
import trigger_manager

state_manager.init()
time_manager.init()
trigger_manager.init()
interface_manager.init()
boids.init()

interface_manager.loop()
