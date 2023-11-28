import pymunk
import pygame

from Agent.Agent2 import *
from Physics.arm import *
from Physics.arm2 import *
from Physics.polygon import *
from Physics.utils import *
import math
import time

pygame.init()

display= pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
space=pymunk.Space()
space.gravity=(0,1000)
fps=60


class Arm():
    def __init__(self, space, armPosition, armLength, rotation, group=1):
        self.space = space
     
     
        self.complete = False
        self.CurrentAngles = []
        self.ExpectedAngles = []
        self.Objects = []


        self.collisionType = group
        self.shapeFilter = pymunk.ShapeFilter(group=1)

        anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
        anchor.position = armPosition
        armPositionX,armPositionY=armPosition
        armPosition=(armPositionX, armPositionY+armLength/2)

        self.createArm(armPosition,armLength,anchor,(0,0),rotation)

 

    def createArm(self,armPosition,armLength,anchor,anchorPosition, rotation):
    
        armMass = MASS_PER_LENGTH*armLength
        arm = pymunk.Body(armMass, pymunk.moment_for_box(armMass, (ARM_WIDTH, armLength)))
        arm.position=armPosition
        armShape = pymunk.Poly.create_box(arm, (ARM_WIDTH, armLength))
        armShape.color = 0, 0, 0, 100
        armShape.filter = self.shapeFilter
        joint = pymunk.PinJoint(arm, anchor, (0, -armLength/2), anchorPosition)
        motor = pymunk.SimpleMotor(arm, anchor, rotation)

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
        


    def addJoint(self, length,rotation, collision_type=None, end=False):
        if self.complete:
            return
    
        prevJoint = self.Objects[-1]
        prevArm = prevJoint["Arm"]
        prevArmX,prevArmY = prevArm.position
        prevArmLength = prevJoint["Length"]
        armPosition=(prevArmX,prevArmY + prevArmLength/2 + length/2)
        prevAnchorPosition=(0,prevArmLength/2)
        self.createArm(armPosition,length,prevArm,prevAnchorPosition,rotation)



        if end:
            self.Objects[-1]["Shape"].collision_type=collision_type

            print(self.Objects[-1]["Shape"].collision_type)
            self.complete = True
            self.CurrentAngles = [0]*len(self.Objects)
            self.diffCounter = [0]*len(self.Objects)
            #self.space.add_collision_handler()


    ## Might need this function for compatibility with other objects.
    def draw(self, display, color = [0, 0, 0]):
        return

pin_joint_created =  {"Arm_1": False, "Arm_2": False}
global_count=0 

def on_collision_arbiter_begin(arbiter, space, data):


    if arbiter.shapes[0].collision_type == 40:
        polygon= arbiter.shapes[0]
        arm=arbiter.shapes[1]
    elif arbiter.shapes[1].collision_type == 40:
        polygon=arbiter.shapes[1]
        arm=arbiter.shapes[0]


    closest_arm = None
    min_distance = float('inf')
    arm_key=None

    for key in data.get("arms_data"):
        contact_point = arbiter.contact_point_set.points[0].point_a

        current_arm = data.get("arms_data")[key]["Arm"]
        print(current_arm)
       
        current_arm_length = data.get("arms_data")[key]["Length"]
        end_of_current_arm = current_arm.position + (0, current_arm_length / 2)
      
        distance = math.sqrt(
            (end_of_current_arm.x - contact_point.x) ** 2 + (end_of_current_arm.y - contact_point.y) ** 2
        )
    

        if distance < min_distance:
            min_distance = distance
            closest_arm = current_arm
            closest_arm_length= current_arm_length
            arm_key=key
            


    if closest_arm is not None and not pin_joint_created[arm_key]:

        pin_joint = pymunk.PinJoint(closest_arm, polygon.body, (0, closest_arm_length / 2),
                                polygon.body.world_to_local(contact_point))
        space.add(pin_joint)
        pin_joint_created[arm_key] = pin_joint
    print("pinjoint")
    print(pin_joint_created)
    global global_count
    if pin_joint_created["Arm_1"] and pin_joint_created ["Arm_2"]:
        global_count+=1
     
    
    if(global_count==5):
        for keys in pin_joint_created:

            space.remove(pin_joint_created[keys])

     
    


    return False

def post_solve(arbiter, space, data):
    shapes = arbiter.shapes
    polygon_shape = None
    arm_shape = None

    # Check which shape is the polygon and which is the arm
    for shape in shapes:
        if shape.collision_type ==  40:
            polygon_shape = shape
        elif shape.collision_type == 20:
            arm_shape = shape
    print("shapes")
    print(arm_shape)
    print(polygon_shape)
    arm_body = arm_shape.body
    polygon_body = polygon_shape.body

    anchor_point_arm = arm_body.position  
    anchor_point_polygon = polygon_body.position  


    pin_joint = pymunk.PinJoint(arm_body, polygon_body, anchor_point_arm, anchor_point_polygon)


    space.add(pin_joint)
 
    pass


def game():
    window = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    d_options = pymunk.pygame_util.DrawOptions(window)
    clock = pygame.time.Clock()
    
    addFloor(space)

    agentActive = 60

    collisionTypePolygon=40

    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]],collisionTypePolygon)

    collisionTypeArm=20



    arm1 = Arm(space, (20, 250),100,-0.1)
    arm1.addJoint(100,-0.3,collisionTypeArm,True)

    arm2 = Arm(space, (340, 250),100,0.1)
    arm2.addJoint(100,0.3,collisionTypeArm,True)

    handler = space.add_collision_handler(collisionTypePolygon, collisionTypeArm)  
    handler.begin = on_collision_arbiter_begin




 

    arms = [arm1,arm2]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        space.step(1/fps)
        display.fill((255,255,255))
        polygon.draw(window)
        draw(space, window, d_options)
        arms_data = {"Arm_1": (arm1.Objects[-1]), "Arm_2": (arm2.Objects[-1])}
        handler.data["arms_data"] = arms_data


        clock.tick(fps)


def draw(space, window, draw_options):
    window.fill((255,255,255))
    space.debug_draw(draw_options)
    pygame.display.update()


game()
pygame.quit()

