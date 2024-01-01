from vpython import *
import time

for i in range(100):
    mybox = box(texture = textures.stucco, 
                axis = vector(1, 2, 2),
                pos= vector(-1, 2, 2), 
                up = vector(-1, 2, 2)) 
    time.sleep(0.5)
