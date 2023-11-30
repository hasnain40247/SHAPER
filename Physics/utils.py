## Utility file. 
## Constant defenitions and utility functions

import pymunk
import pygame
import pymunk.pygame_util
import random


PI = 355/113 ## Fancy approximation for Pi
HEIGHT = 850
WIDTH = 1500
WALL_THICKNESS = 10
FPS = 60.0
DT = 1.0/FPS
THICKNESS_OF_ARM = 10

## Used to setup the collision type for the polygon. 
POLYGON_COLL_TYPE = 0

def radsToDegree(data):
    return (data*57.2957795) % 360.0

def DegreesToRads(data):
    return data*(2*PI/360) % (2*PI)

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
def addPolygon(space, points, position=(HEIGHT/2,WIDTH/2), sides=[],mass = 10):
    body = pymunk.Body()
    body.position = position
    
    shape = pymunk.Poly(body, points)
    shape.friction = 0.5
    shape.collision_type = pymunk.COLLTYPE_DEFAULT
    space.add(body, shape)


def addFloor(space):
    ## Attaching it to the Golbal pymunk body. Also made it extend horizontally for safety :)
    floor = pymunk.Poly(space.static_body, [(WIDTH+100,HEIGHT),(-100,HEIGHT),(WIDTH+100,HEIGHT-25),(-100,HEIGHT-25)])
    floor.friction = 0.9
    space.add(floor)

def custom_gravity_velocity(body, gravity, damping, dt):
    g = (0, 1000)
    # Call the default velocity function with the new gravity
    pymunk.Body.update_velocity(body, g, damping, dt)
