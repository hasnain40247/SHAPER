import pymunk
import pygame
from Physics.utils import *

class ArmSection():
    def __init__(self, space, body1, body2, anchor=False):
        self.body1 = body1.body
        self.body2 = None
        if not anchor:
            self.body2 = body2.body
        else:
            ## As its an anchor it is set as an STATIC Object. 
            self.body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
            self.body2.position = body2
        joint = pymunk.PinJoint(self.body1, self.body2)
        space.add(joint)

    def draw(self, display, color=(255,255,255)):
        p1 = convertCoordinartes(self.body1.position)
        p2 = convertCoordinartes(self.body2.position)
        pygame.draw.line(display, color, p1, p2, THICKNESS_OF_ARM)
