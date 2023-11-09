import pymunk
from Physics.utils import *
from math import atan2
from Physics.gripper import *
from Physics.armsection import *
from Physics.ball import *

def getAngle(body1, body2=None):
    if body2 == None:
        return body1.angle
    return atan2(body2.position[1]-body1.position[1], body2.position[0]-body1.position[0])

## The arm the can be used to manipulate the objects in the frame.
## Will have n joints. One will be at the original position and the other sat a distance from the previous.
## The end effector can grab objects by changing its friction. It can also grab them fully by forming a pin join between it and the other body. 
class Arm:
    def __init__(self, space, position, end=False):
        ## The static point where the arm starts. This point doesnt change.
        self.Anchor = position
        ## Holds all the objects and the constrains related to this arm. 
        ## When the arm is holding an external object, its constrain will be handled elsewhere as more than one object can grab the polygon.
        self.Objects = list()
        self.Joints = list()
        ## Set complete to True only after all the joints are initialzed.
        self.complete = False


        ## The current angle is set to the angle of the 
        self.CurrentAngle = []
        self.ExpectedAngle = []

        self.space = space
        

    def addJoint(self, distanceFromPrevious, end=False):
        if self.complete:
            print("Its already built. Re initialize the arm.")
            return
        if len(self.Objects) == 0:
            ## First joint need to be added
            if end:
                ## Only one jointed arm. 
                gripper = Gripper(self.space, (self.Anchor[0], self.Anchor[1]+distanceFromPrevious))
                joint = ArmSection(self.space, gripper, self.Anchor, True)

                self.Joints.append(joint)
                self.Objects.append(gripper)
                
                self.CurrentAngle.append(getAngle(joint.body1, joint.body2))
                self.ExpectedAngle.append(0.0)
                
                self.complete = True
            else:
                ball = Ball(self.space, (self.Anchor[0], self.Anchor[1]+distanceFromPrevious))
                joint = ArmSection(self.space, ball, self.Anchor, True)

                self.Joints.append(joint)
                self.Objects.append(ball)

                self.CurrentAngle.append(getAngle(joint.body1, joint.body2))
                self.ExpectedAngle.append(0.0)
        else:
            if end:
                prevBody = self.Objects[-1]
                gripper = Gripper(self.space, (prevBody.body.position[0], prevBody.body.position[1]+distanceFromPrevious))
                joint = ArmSection(self.space, gripper, prevBody, False)

                self.Joints.append(joint)
                self.Objects.append(gripper)

                self.CurrentAngle.append(getAngle(joint.body1, joint.body2))
                self.ExpectedAngle.append(0.0)

                self.complete = True
            else:
                prevBody = self.Objects[-1]
                ball = Ball(self.space, (prevBody.body.position[0], prevBody.body.position[1]+distanceFromPrevious))
                joint = ArmSection(self.space, ball, prevBody, False)

                self.Joints.append(joint)
                self.Objects.append(ball)

                self.CurrentAngle.append(getAngle(joint.body1, joint.body2))
                self.ExpectedAngle.append(0.0)

    def __repr__(self) -> str:
        out = ""
        for obj in self.Objects:
            out += repr(obj)

        return out
    
    def updateCurrentAngles(self):
        for idx in range(len(self.Joints)):
            joint = self.Joints[idx]
            self.CurrentAngle[idx] = getAngle(joint.body1, joint.body2)


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

    ## Renders the object on the window.
    ## But also updates the current angles. 
    def draw(self, display, verbose=False):
        self.updateCurrentAngles()
        for obj in self.Objects:
            obj.draw(display)
        for j in self.Joints:
            j.draw(display)  
        if verbose:
            for idx in range(len(self.CurrentAngle)):
                print(radsToDegree(self.CurrentAngle[idx]))

class ArmSection():
    ## If anchor is set to True body2 must be a position
    ## If anchor is False body2 must be pymunk body.
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

    def __repr__(self) -> str:
        return "Ball"

class Gripper(Ball):
    def __init__(self, space, postion):
        super().__init__(space, postion)
        
    def rough(self):
        self.shape.friction = 1

    def smooth(self):
        self.shape.friction = 0.25
    
    def draw(self, display):
        pygame.draw.circle(display, (0, 0, 0), convertCoordinartes(self.body.position), RADIUS_OF_GRIPPER)
        #super().draw(display, (0, 0, 0))

    def grab(self):
        ## Check if the gripper is touching the polygon
        ## Create a pivot constraint and return it. The constraint will be added to the space.
        pass

    def __repr__(self) -> str:
        return "Gripper"


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
    
