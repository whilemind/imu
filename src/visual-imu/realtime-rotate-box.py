from vpython import *
import time

box_axis = vec(1,2,2)
box_pos = vector(-1, 2, 2)
box_size = vector(25, 1, 12)

mybox = box(texture = textures.metal, 
            axis = box_axis,
            pos = box_pos,
            size = box_size)
 
r = vector(0, 2, 2)
for i in range(10):
    # r.x = i
    # mybox.pos = r
    mybox.rotate(angle=i, axis=r)
    time.sleep(0.5)

