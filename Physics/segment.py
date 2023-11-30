import pymunk
import pygame
from Physics.utils import *
from math import atan2
import math

class BoxSegment():
    def __init__(self, space, start, end, horiz=False, collision_type=50):
        self.body = pymunk.Body(pymunk.Body.STATIC)
        self.body.position = (start[0]+end[0])/2, (start[1]+end[1])/2 

        newShape = None
        if horiz:
            newShape = pymunk.Poly.create_box(self.body, (abs(end[0] - start[0]), 10))
        else:
            newShape = pymunk.Poly.create_box(self.body, (10, abs(end[0] - start[0])))
        newShape.color = 0, 0, 0, 20
        newShape.collision_type = collision_type

        space.add(newShape, self.body)

    
