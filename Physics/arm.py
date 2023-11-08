import pymunk
from Physics.utils import *
from math import atan2
from Physics.gripper import *
from Physics.armsection import *
from Physics.ball import *

def getAngle(body1, body2):
    return atan2(body2.position[1]-body1.position[1], body2.position[0]-body1.position[0])

## The arm the can be used to manipulate the objects in the frame.
## Will have n joints. One will be at the original position and the other sat a distance from the previous.
## The end effector can grab objects by changing its friction. It can also grab them fully by forming a pin join between it and the other body. 
class Arm:
    def __init__(self, space, position):
        ## The static point where the arm starts. This point doesnt change.
        self.Anchor = position
        ## Holds all the objects and the constrains related to this arm. 
        ## When the arm is holding an external object, its constrain will be handled elsewhere as more than one object can grab the polygon.
        self.Objects = list()
        self.Joints = list()
        ## Set complete to True only after all the joints are initialzed.
        self.complete = False

        self.CurrentAngle = []
        self.ExpectedAngle = []

        self.space = space

        # if end:
        #     gripper = Gripper(space, (position[0]+armLenght, position[1]))
        #     joint1 = ArmSection(space, gripper, (position[0], position[1]), True)

        #     self.complete = True

        #     self.Objects.append(gripper)
        #     self.Joints.append(joint1)
        #     self.CurrentAngle.append(getAngle(gripper.body, joint1.body2))
        #     self.ExpectedAngle = [0]

        # else:
        #     ball1 = Ball(space, (position[0]+armLenght, position[1]))
        #     joint1 = ArmSection(space, ball1, position, True)

        #     self.Objects.append(ball1)
        #     self.Joints.append(joint1)
        #     self.CurrentAngle.append(getAngle(ball1.body, joint1.body2))
        #     self.ExpectedAngle.append(0)
        

    def addJoint(self, distanceFromPrevious, end=False):
        space = self.space
        if len(self.Objects) > 0:
            prevBody = self.Objects[-1]
            prevPosition = prevBody.body.position
        else :
            prevBody = None
            prevPosition = self.Anchor
        if not end:
            ball1 = Ball(space, (prevPosition[0]+distanceFromPrevious, prevPosition[1]))
            joint1 = ArmSection(space, ball1, prevPosition, True)

            self.Objects.append(ball1)
            self.Joints.append(joint1)

            self.ExpectedAngle.append(0)
            self.CurrentAngle.append(getAngle(ball1.body, joint1.newPoint))
        else: 

            gripper = Gripper(space, (prevPosition[0]+distanceFromPrevious, prevPosition[1]))
            joint1 = ArmSection(space, gripper, prevBody, False)

            self.Objects.append(gripper)
            self.Joints.append(joint1)

            self.ExpectedAngle.append(0)
            self.CurrentAngle.append(getAngle(gripper.body, joint1.newPoint))
            self.complete = True
    

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
        for j in self.Joints:
            j.draw(display)  

# if __name__ == "__main__":
#     space = pymunk.Space()

#     a = Arm(space, (100, 100))
    
