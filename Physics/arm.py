import pymunk
import pygame
from Physics.utils import *
from functools import reduce
from math import atan2
from Physics.objectPosition import hitEdge

## The arm the can be used to manipulate the objects in the frame.
## Will have two joins. One will be at the original position and the other at a distance from the first
## The end effor can grab objects by chaing its friction. 
class Arm:
    def __init__(self, space, position):
        self.Anchor = position
        self.Objects = list()

        ball1 = Ball(space, (position[0]+150, position[1]))
        gripper = Gripper(space, (position[0]+350, position[1]))

        joint1 = ArmSection(space, ball1, position, True)
        joint2 = ArmSection(space, ball1, gripper, False)

        ## These vraibles are controlled by the physics.
        self.CurrentAngle = [0,0]
        
        ## These variables are controlled by the agent. No limits on the movement.
        ## Limits and end stops need to be added in the future.
        self.ExpectedAngle = [0,0]

        self.gripper = False
        self.friction = 0

        self.Objects.extend([ball1, gripper, joint1, joint2])

    def getNextStep(self):
        diff = list(map(lambda x: (x[0]-x[1])/ARMSPEED, zip(self.ExpectedAngle,self.CurrentAngle)))        
        diff = list(map(lambda x: x[0]+x[1], zip(self.CurrentAngle, diff)))
        return diff
                
    def rough(self):
        self.gripper.rough()

    def smooth(self):
        self.gripper.smooth()

    ## This functon runs the simulation but doesnt render it.
    ## makes it faster. 
    ## only updates the variables in the class. Will not call .draw() methods.
    def drawInternal(self):
        pass

    ## Returns the current state of the arm.
    ## This will be theh input to the agent.
    def getAttitude(self):
        return self.CurrentAngle

    ## Uses the AI output to set the desired angles and the gripper state. 
    def setDesiriedAttitude(self, setAttitude):
        self.ExpectedAngle = setAttitude

    def draw(self, display):
        for obj in self.Objects:
            obj.draw(display)

class ArmSection():
    def __init__(self, space, body1, body2, anchor=False):
        self.body1 = body1.body
        if not anchor:
            self.body2 = body2.body
        else:
            self.body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
            self.body2.position = body2
        joint = pymunk.PinJoint(self.body1, self.body2)
        space.add(joint)

    def draw(self, display, color=(255,255,255)):
        p1 = convertCoordinartes(self.body1.position)
        p2 = convertCoordinartes(self.body2.position)
        pygame.draw.line(display, color, p1, p2, THICKNESS_OF_ARM)


class Ball():
    def __init__(self, space, position):
        self.body = pymunk.Body()
        self.body.position = position[0], position[1]
        self.shape = pymunk.Circle(self.body, RADIUS_OF_GRIPPER)
        self.shape.density = 1
        self.shape.friction = 1
        space.add(self.body, self.shape)

    def draw(self, display, color=(0,0,255)):
        pygame.draw.circle(display, color, convertCoordinartes(self.body.position), RADIUS_OF_GRIPPER)

class Gripper(Ball):
    def __init__(self, space, postion):
        super().__init__(space, postion)
        
    def rough(self):
        self.shape.friction = 1

    def smooth(self):
        self.shape.friction = 0.25
    
    def draw(self, display):
        super().draw(display, (0, 255, 0))

    def grab(self):
        ## Check if the gripper is touching the polygon
        ## If it is add the pivot joint to between them and return them
        ## We incorporate it with PyMunk and it should work
        pass


class Polygon():
    def __init__(self, space, originalAngle, goalAngle, points):
        self.orginal = originalAngle
        self.goal = goalAngle
        self.currentAngle = originalAngle

        self.points = points
        
        positionX = 0
        positionY = 0
        for idx in range(len(points)):
            positionX += points[idx][0]
            positionY += points[idx][1]

        positionX = positionX/len(points)
        positionY = positionY/len(points)

        self.body = pymunk.Body()
        self.body.position = positionX, positionY
        self.body.angle = atan2(originalAngle[1],originalAngle[0])
        self.shape = pymunk.Poly(self.body, self.points)
        self.shape.density = 1
        self.shape.friction = 1
        space.add(self.body, self.shape)


    def draw(self, display, color=(255,255,255)):
        pygame.draw.polygon(display, color, list(map(convertCoordinartes, self.points)))


    ## We need more fucntions like so to extract the required inputs to the agents.
    ## Think of all the details the agent might need reaggarding the object and implement them.
    def getCurrentPosition(self):
        return self.body.position
    
    def getCurrentVelocity(self):
        return self.body.velocity_at_world_point
    

if __name__ == "__main__":
    space = pymunk.Space()

    a = Arm(space, (100, 100))
    
