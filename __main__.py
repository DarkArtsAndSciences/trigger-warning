import boids
import time_manager
import trigger_manager
import interface_manager

boids.init()
time_manager.init()
trigger_manager.init()
interface_manager.init()

interface_manager.loop()
