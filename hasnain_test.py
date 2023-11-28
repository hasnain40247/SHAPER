import pymunk
import pygame

from Agent.Agent2 import *
from Physics.arm import *
from Physics.arm2 import *
from Physics.polygon import *
from Physics.utils import *



pygame.init()

display= pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
space=pymunk.Space()
space.gravity=(0,1000)
fps=25
polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

class Arm():
    def __init__(self, space, armPosition, armLength, group=1):
        self.space = space
     
     
        self.complete = False
        self.CurrentAngles = []
        self.ExpectedAngles = []
        self.Objects = []


        self.colisionType = group
        self.shapeFilter = pymunk.ShapeFilter(group=1)

        anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
        anchor.position = armPosition
        armPositionX,armPositionY=armPosition
        armPosition=(armPositionX, armPositionY+armLength/2)

        self.createArm(armPosition,armLength,anchor,(0,0))


    def createArm(self,armPosition,armLength,anchor,anchorPosition):
    
        armMass = MASS_PER_LENGTH*armLength
        arm = pymunk.Body(armMass, pymunk.moment_for_box(armMass, (ARM_WIDTH, armLength)))
        arm.position=armPosition
        armShape = pymunk.Poly.create_box(arm, (ARM_WIDTH, armLength))
        armShape.color = 0, 0, 0, 100
        armShape.filter = self.shapeFilter
        joint = pymunk.PinJoint(arm, anchor, (0, -armLength/2), anchorPosition)
        motor = pymunk.SimpleMotor(arm, anchor, 0.5)

        self.Objects.append({
                                "Arm":arm,
                                "Motor": motor,
                                "Middle" : armPosition,
                                "Length": armLength,
                                "Shape": armShape
                            })
        self.space.add(arm)
        self.space.add(armShape)
        self.space.add(joint)
        self.space.add(motor)
        


    def addJoint(self, length, end=False):
        if self.complete:
            return
    
        prevJoint = self.Objects[-1]
        prevArm = prevJoint["Arm"]
        prevArmX,prevArmY = prevArm.position
        prevArmLength = prevJoint["Length"]
        armPosition=(prevArmX,prevArmY + prevArmLength/2 + length/2)
        prevAnchorPosition=(0,prevArmLength/2)
        self.createArm(armPosition,length,prevArm,prevAnchorPosition)

     
        if end:
            self.complete = True
            self.CurrentAngles = [0]*len(self.Objects)
            self.diffCounter = [0]*len(self.Objects)
            #self.space.add_collision_handler()


    ## Might need this function for compatibility with other objects.
    def draw(self, display, color = [0, 0, 0]):
        return
    
    def preHit(self, arbiter, space, data):
        print("Pre hit called for arm")
        pass

    def grab(self):
        ## Find the collision between the last arm segment and the polygon. 
        ## If collision present or distance is small then add a pin constrain on them.
        terminalArmSegment = self.Objects[-1]




    






def game():
    window = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    d_options = pymunk.pygame_util.DrawOptions(window)
    clock = pygame.time.Clock()
    
    addFloor(space)

    agentActive = 60

    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

    arms = []

    arm1 = Arm(space, (450, 250),100)
    arm1.addJoint(100)




    arms = [arm1]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        space.step(1/fps)
        display.fill((255,255,255))
        polygon.draw(window)
        draw(space, window, d_options)
        clock.tick(fps)


def draw(space, window, draw_options):
    window.fill((255,255,255))
    space.debug_draw(draw_options)
    pygame.display.update()


game()
pygame.quit()

