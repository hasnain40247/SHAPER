import pymunk
import pygame
from Physics.utils import *

class ArmSection():
    def __init__(self, space, anchorPoint, newPoint, anchor=False):
        self.anchorPoint = anchorPoint.body
        self.newPoint = None
        if not anchor:
            self.newPoint = newPoint.body
        else:
            ## As its an anchor it is set as an STATIC Object. 
            self.newPoint = pymunk.Body(body_type=pymunk.Body.STATIC)
            self.newPoint.position = newPoint
        joint = pymunk.PinJoint(self.anchorPoint, self.newPoint)
        space.add(joint)

    def draw(self, display, color=(255,255,255)):
        p1 = convertCoordinartes(self.anchorPoint.position)
        p2 = convertCoordinartes(self.newPoint.position)
        pygame.draw.line(display, color, p1, p2, THICKNESS_OF_ARM)
