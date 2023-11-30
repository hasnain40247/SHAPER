import pymunk
import pygame
import pymunk.pygame_util
from Agent.Agent import *
from Physics.arm import *
from Physics.polygon import *
from Physics.segment import *
from Physics.utils import *

PHYSICS_FPS = 25

## Setup the envirnment.
def setup():
    pygame.init()

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    space = pymunk.Space()
    space.gravity = (0, 1000)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    ## Window is the pygame window used to render the objects
    ## Space is the pymunk saimulation space. All the physics are calculated in this space.
    ## Draw_options connects the above two so that the space can be rendered in the window.
    return window, space, draw_options


afterKFrames = 300

## Function in which all the environment is simulated. 
def run(window, space, width=WIDTH, height=HEIGHT):
    run = True
    clock = pygame.time.Clock()
    
    addFloor(space)

    # a = BoxSegment(space, (WALL_THICKNESS, HEIGHT-WALL_THICKNESS), (WALL_THICKNESS, WALL_THICKNESS), True)
    # b = BoxSegment(space, (WALL_THICKNESS, WALL_THICKNESS), (WIDTH-WALL_THICKNESS, WALL_THICKNESS), False)
    # c = BoxSegment(space, (WIDTH-WALL_THICKNESS, WALL_THICKNESS), (WIDTH-WALL_THICKNESS, HEIGHT-WALL_THICKNESS), True)
    # d = BoxSegment(space, (WALL_THICKNESS, WIDTH-WALL_THICKNESS), (WIDTH-WALL_THICKNESS, HEIGHT-WALL_THICKNESS), False)
    

    ## The object that needs to be grabbed and fondled
    polygon = Polygon(space, 0, [[100, 100], [200, 100], [200, 200]])

    arms = []

    arm1 = Arm(space, (250, 250))
    arm1.addJoint(100)
    arm1.addJoint(50)
    arm1.addJoint(50,rotation=0.6, end=True)

    arm2 = Arm(space, (350, 250),2)
    arm2.addJoint(150)
    arm2.addJoint(100)
    arm2.addJoint(50,rotation=1.2, end=True)


    arm3 = Arm(space, (500, 50),3)
    arm3.addJoint(250)
    arm3.addJoint(150)
    arm3.addJoint(100,rotation=0.6, end=True)

    arms = [arm1, arm2, arm3]

    #arm.dropPolygon() ## Works

    armData = {"Arm_1": (arm1, True), "Arm_2": (arm2, True), "Arm_3": (arm3, True)} ## modify this to grab stuff
    collision = space.add_collision_handler(40, 20) #hard coded these since by default the collision type of arm and polygon is set to 20 and 40 respectively.
    collision.begin = polygon.on_collision_arbiter_begin #arm is an object of class Arm1
    
    collisionWithBox = space.add_collision_handler(40, 50)
    
    ## There is a problem. If we render every frame it looks janky. 
    ## Fix is to run the physics engine at 600Hz and render the stuff at 60Hz.
    ## We also need to set a rate for the AI to run in the background. When the agent responds the physics engine will react.

    frameNumber = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        collision.data["polygon"] = polygon.body # polygon is an object of Polygon
        collision.data["arms_data"] = armData # armData is a disctionary that contains the information about arms.
       
        ## Render only some of the frames. Makes it more smoother.
        for x in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))

        polygon.draw(window)
        draw(space, window, draw_options)
        clock.tick(FPS)

        if frameNumber > 110:
            arm1.dropPolygon()
            arm2.dropPolygon()
            armData = {"Arm_1": (arm1, False), "Arm_2": (arm2, False), "Arm_3": (arm3, False)} ## modify this to grab stuff

        frameNumber += 1
    pygame.quit()

## Only call this function when we need to render the objects. In most cases rendering it is not needed.
## Call it every frame that needs to be rendered.
def draw(space, window, draw_options):
    window.fill((255,255,255))
    space.debug_draw(draw_options)
    pygame.display.update()

if __name__ == "__main__":
    window, space, draw_options = setup()
    run(window, space)