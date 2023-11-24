import pymunk
from pymunk import SimpleMotor
#from Physics.utils import *
from math import atan2
#from Physics.gripper import *
#from Physics.armsection import *
#from Physics.ball import *


MASS_PER_LENGTH = 10
ARM_WIDTH = 10
PI = 355/113 ## Fancy approximation for Pi


## PID settings
P_ = 1.9
D_ = -0.5
I_ = 0.0005

class Arm1():
    def __init__(self, space, anchorPoistion, group=1):
        self.space = space
        if len(anchorPoistion) != 2:
            print("Error size incorrect")
            return
        self.anchor = anchorPoistion
        self.complete = False

        self.CurrentAngles = []
        self.ExpectedAngles = []

        self.Objects = []
        self.collType = group
        self.shapeFilter = pymunk.ShapeFilter(group=1)


        ## Number of frames since the expected angles were set.
        ## This variable will be rest every time the SetAngles function is called.
        ## It will be incremented every time the arbiter is executed successfully. 
        self.diffCounter = []

    def addJoint(self, length, end=False):
        if self.complete:
            return
        if len(self.Objects) == 0: 
            ## Need to add an anchor.

            ## Generate the anchor.
            newAnchor = pymunk.Body(body_type=pymunk.Body.STATIC)
            newAnchor.position = self.anchor

            ## Generate the mass of the body.
            armMass = MASS_PER_LENGTH*length
            ## Create the body.
            newArmObject = pymunk.Body(armMass, pymunk.moment_for_box(armMass, (ARM_WIDTH, length)))
            newArmObject.position = self.anchor[0], self.anchor[1]+length/2

            ## Create the shape for the object.
            newArmShape = pymunk.Poly.create_box(newArmObject, (ARM_WIDTH, length))
            newArmShape.color = 0, 0, 0, 100

            ## Add constrains and motors to the bodies.
            newJoint = pymunk.PinJoint(newArmObject, newAnchor, (0, -length/2), (0, 0))
            newMotor = pymunk.SimpleMotor(newArmObject, newAnchor, 0.0)

            ## Disable colisions between the arms. 
            ## Might remove this based on hhow the model performs.
            newArmShape.filter = self.shapeFilter

            ## Also add some meta data here. Makes it easier for rendering.
            self.Objects.append({
                                "Object":newArmObject,
                                "Motor": newMotor,
                                "Middle" : (self.anchor[0], self.anchor[1]+length/2),
                                "Length": length
                                })

            ## Add all the objects and shapes to the space.
            self.space.add(newArmObject)
            self.space.add(newArmShape)
            self.space.add(newJoint)
            self.space.add(newMotor)

        else:
            ## Need to add a new arm.

            prevBody = self.Objects[-1].get("Object")
            prevPosition = prevBody.position
            prevLength = self.Objects[-1].get("Length")

            ## Generate the mass of the body.
            armMass = MASS_PER_LENGTH*length
            ## Create the body.
            newArmObject = pymunk.Body(armMass, pymunk.moment_for_box(armMass, (ARM_WIDTH, length)))
            newArmObject.position = prevPosition[0], prevPosition[1]+prevLength/2+length/2

            ## Create the shape for the object.
            newArmShape = pymunk.Poly.create_box(newArmObject, (ARM_WIDTH, length))
            newArmShape.color = 0, 0, 0, 100

            ## Add constrains and motors to the bodies.
            newJoint = pymunk.PinJoint(newArmObject, prevBody, (0, -length/2), (0, prevLength/2))
            newMotor = pymunk.SimpleMotor(newArmObject, prevBody, 0.0)

            ## Disable colision between the arms.
            newArmShape.filter = self.shapeFilter

            ## Also add some meta data here. Makes it easier for rendering.
            self.Objects.append({
                                "Object":newArmObject,
                                "Motor": newMotor,
                                "Middle" : (prevPosition[0], prevPosition[1]+prevLength/2+length/2),
                                "Length": length,
                                "Shape": newArmShape
                            })
            self.space.add(newArmObject)
            self.space.add(newArmShape)
            self.space.add(newJoint)
            self.space.add(newMotor)
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


    ## Inputs are between -1 and 1, convert it to 0 to 2PI
    ## Converts the agent's output to a format that the physics engine can work with.
    def agentToPhysics(self):
        inputs = list(map(lambda x: ((x+1)/2.0)*2*PI, inputs))
        return inputs
    

    ## Converts the data from the physcis engine to a format that can be processed by the agent
    ## Normalize the angles and the position of the bodies. Convert to radians if necessary.
    def physicsToAgent(self):
        pass

    ## Set the expected angles.
    def setAngles(self, inputs):
        if not self.complete:
            return
        if len(inputs) != len(self.Objects):
            return
        ## Clip it between 0 and 2PI
        inputs = list(map(lambda x: x%(2*PI), inputs))
        self.ExpectedAngles = inputs
        self.diffCounter = [0]*len(self.Objects)

    ## Get the current angles
    def getAngles(self):
        for objectIdx in range(len(self.Objects)):
            self.CurrentAngles[objectIdx] = self.Objects[objectIdx]["Object"].angle
        self.arbiterAgent()
        #print("Current angle:", self.CurrentAngles, "Expected angle:", self.ExpectedAngles)
        return self.CurrentAngles
    
    # Once we get the data from the agent we need the physics engine to execute it.
    # This function uses a simple PID system to achieve that. 
    # DIFF = (EXPECTED - CURRENT)
    def arbiterAgent(self):
        if len(self.ExpectedAngles) == 0:
            return
        diff = list(map(lambda x: x[1]-x[0], zip(self.CurrentAngles, self.ExpectedAngles)))
        for objIdx in range(len(self.Objects)):
            if diff[objIdx] < 10**-6:
                continue
            self.diffCounter[objIdx] += diff[objIdx]
            self.Objects[objIdx]["Motor"].rate = P_*diff[objIdx] + D_*self.Objects[objIdx]["Motor"].rate + I_*self.diffCounter[objIdx]


if __name__ == "__main__":
    space = pymunk.Space()
    arm = Arm1(space, (250, 250))
    arm.addJoint(100)
    arm.addJoint(100, True)

    curAngles = arm.getAngles()
    print("Current Angles:", curAngles)

    arm.setAngles([3.14, 0])

    while True:
        curAngles = arm.getAngles()
        print("Current Angles:", curAngles)