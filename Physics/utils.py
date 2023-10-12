## Utility file. 
## Constant defenitions and utility functions

import pymunk
import pygame
import pymunk.pygame_util
import random 


HEIGHT = 800
WIDTH = 1000
FPS = 60.0
DT = 1.0/FPS
RADIUS_OF_GRIPPER = 20
RADIUS_OF_JOINT = 10
THICKNESS_OF_ARM = 10

def convertCoordinartes(position):
    return int(position[0]), int(HEIGHT-position[1])

## Function to create a circle. Used to test the physics.
## The body is the underlying object on which the physics is calculated.
## Shape is used to represent the body so that it can be rendered.
def addCircle(space, position=(HEIGHT/2,WIDTH/2), radius=10, mass = 10):
    body = pymunk.Body()
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    # Sets random color.
    shape.color = tuple([random.randint(1,255)]*3 + [100])
    space.add(body, shape)
    return shape


## TODO
def addPolygon(space, position=(HEIGHT/2,WIDTH/2), sides=[],mass = 10):
    pass
