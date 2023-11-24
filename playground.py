import pymunk
import pygame
import pymunk.pygame_util
from Physics.arm import *
from Physics.arm2 import *
from Physics.polygon import *
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

    ## shapeFilter = pymunk.ShapeFilter(group=1)
    ## The object that needs to be grabbed and fondled
    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

    # arm1 = Arm1(space, (250, 205))
    # arm1.addJoint(100)
    # arm1.addJoint(200, True)

    # arm2 = Arm1(space, (300, 250),2)
    # arm2.addJoint(150)
    # arm2.addJoint(100)
    # arm2.addJoint(50, True)


    arm3 = Arm1(space, (500, 500),3)
    arm3.addJoint(150)
    arm3.addJoint(75)
    arm3.addJoint(50, True)


    ## There is a problem. If we render every frame it looks janky. 
    ## Fix is to run the physics engine at 600Hz and render the stuff at 60Hz.
    ## We also need to set a rate for the AI to run in the background. When the agent responds the physics engine will react.

    frameNumber = 0
    flag = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        ## Render only some of the frames. Makes it more smoother.
        for x in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))

        if frameNumber > afterKFrames and not flag:
            print("Setting angles")
            # arm1.setAngles([0, 0.8])
            # arm2.setAngles([3.14, 3.14, 3.14])
            arm3.setAngles([1.6, 3.0, 0])
            flag = not flag

        # arm1.getAngles()
        # arm2.getAngles()
        arm3.getAngles() 
        polygon.draw(window)
        draw(space, window, draw_options)
        clock.tick(FPS)

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