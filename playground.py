import pymunk
import pygame
import pymunk.pygame_util
from Physics.arm import *
from Physics.polygon import *
from Physics.utils import *

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


## Function in which all the environment is simulated. 
def run(window, space, width=WIDTH, height=HEIGHT):
    run = True
    clock = pygame.time.Clock()
    
    addFloor(space)

    ## Create two arms.
    ## They are unpowered so they swing like you know
    arm1 = Arm(space, (50, 500), 100, False)
    #arm1.addJoint(50, armType=0, end = False)
    arm1.addJoint(50, armType=0, end = True)
    
    arm2 = Arm(space, (WIDTH-50, 500), 200, True)

    ## The object that needs to be grabbed and fondled
    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        arm1.draw(window)
        arm2.draw(window)
        polygon.draw(window)
        draw(space, window, draw_options)
        space.step(DT)
        clock.tick(FPS)

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