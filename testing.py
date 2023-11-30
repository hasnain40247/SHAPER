import pymunk
import pygame
import pymunk.pygame_util
from Agent.agent import *
from Physics.arm import *
from Physics.arm import *
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


## Function in which all the environment is simulated. 
def run(window, space, path=None, width=WIDTH, height=HEIGHT):
    run = True
    clock = pygame.time.Clock()
    
    ## Make an agegnt.
    agent = Agent()

    ## Add all the layers as required.
    lAgent = Agent()
    lAgent.addLayer("Input", 61, None, False)
    lAgent.addLayer("H0", 512, Linear, False)
    lAgent.addLayer("H1", 256, Sigmoid, False)
    lAgent.addLayer("H2", 128, TanH, False)
    lAgent.addLayer("H3", 64, Sigmoid, False)
    lAgent.addLayer("Output", 12, None, True)

    if path != None:
        try:
            agent.load(path)
        except FileNotFoundError:
            print("Error finding finding file")
            raise FileExistsError 
    ## Every 10 frames the agent gives an output to the engine.
    agentActive = 10


    ## The object that needs to be grabbed and fondled
    polygon = Polygon(space, 0.8, [[600, 50], [680, 50], [600, 250]])

    print("Current position:", polygon.getCurrentPosition())

    goalState = (
            0.0, #Angle
            150, 150, # poosition of the body
    )

    arms = []

    arm1 = Arm(space, (200, 100))
    arm1.addJoint(250)
    arm1.addJoint(250)
    arm1.addJoint(100, True)

    arm2 = Arm(space, (800, 100),2)
    arm2.addJoint(250)
    arm2.addJoint(250)
    arm2.addJoint(100, True)

    arm3 = Arm(space, (1200, 100),3)
    arm3.addJoint(250)
    arm3.addJoint(250)
    arm3.addJoint(100, True)

    arms = [arm1, arm2, arm3]


    ## There is a problem. If we render every frame it looks janky. 
    ## Fix is to run the physics engine at 600Hz and render the stuff at 60Hz.
    ## We also need to set a rate for the AI to run in the background. When the agent responds the physics engine will react.

    frameNumber = 0

    ## Collision handler
    armData = dict()
    ## Set all the with colission enabled.
    for idx, arm in enumerate(arms):
        armData["Arm_" + str(idx+1)] = [arm, True]
    collision = space.add_collision_handler(40, 20) #hard coded these since by default the collision type of arm and polygon is set to 20 and 40 respectively.
    collision.begin = polygon.on_collision_arbiter_begin #arm is an object of class Arm1


    while run:
        print("Current position:", polygon.getCurrentPosition())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        if frameNumber%agentActive == 0:
            ## Agent only controls the arm every n frames.
            inputVector = []
            ## Input involving the arms.
            for arm in arms:
                lTempData = arm.physicsToAgent()
                ## The angle wrt to the sapce
                inputVector.extend(lTempData["Angles"])
                ## angular velocity of each segment
                inputVector.extend(lTempData["Rates"])
                ## Position of the end points of each segment
                inputVector.extend(lTempData["Positions"])
            
            ## Input involving the polygon.
            body = polygon.body
            polygonData = [body.position[0], body.position[1], body.angle, body.angular_velocity]
            inputVector.extend(polygonData)
            
            ## Input regarding the goal.
            inputVector.extend(goalState)

            inputVector = np.array(inputVector)

            ## Get the prediction from the agent.
            rawOut = lAgent.forwardPass(inputVector)
            ## Use the agents output to manipulate the arms.
            k = 0
            for armIdx, arm in enumerate(arms):
                newRates = []
                for _ in range(len(arm.Objects)):
                    newRates.append(rawOut[k])
                    k+=1 
                ## Set the arm speeds
                #arm.agentToPhysics(newRates, 2)

                ## Activate or deactivate the gripper.
                # if rawOut[k] > 0.0:
                #     armData["Arm_" + str(armIdx+1)][1] = True
                # else:
                #     armData["Arm_" + str(armIdx+1)][1] = False
                #     arm.dropPolygon()
                k += 1

        # Render only some of the frames. Makes it more smoother.
        for _ in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))
        
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