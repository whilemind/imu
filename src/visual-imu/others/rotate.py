#!/usr/bin/python
# -*- coding: utf-8 -*-
import visual
visual.scene.width = 500 
visual.scene.heigth = 500 
visual.scene.center = (0,0,0)
visual.scene.title = "Rotate"

cube = visual.box(pos=(0,0,0),axis=(0,0,1),length=0.1,width=0.1,height=0.1,color=visual.color.blue)
visual.box(pos=(1,0,0),axis=(0,0,1),length=0.3,width=0.3,height=0.3,color=visual.color.blue)
while True:
    visual.rate(1)
    visual.scene.forward = visual.scene.forward.rotate(angle=0.095,axis=visual.scene.up)