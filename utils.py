from Agent.agent import *
from Physics.polygon import *
from Physics.arm import *
from Physics.utils import *

## To make sure the agent learns slowly, we need differen scoring functions..

## Scoreing function 1
## The agent needs to learn to catch the object and make sure not to drop it.
## Gives a good score as long as the body was not dropped.
def score1(polygon, goalState, minH=0, minW=0, maxH=HEIGHT, maxW=WIDTH):
    pos = polygon.body.position 

    diffX = abs(pos[0] - (maxW-minW)/2)
    diffY = abs(pos[1] - (maxH-minH)/2)

    diff = diffY + diffX

    return diff


## We do not render stuff when we train as rendering will slow things down.
def initResourcers(goalState):
    ## Initialize the space.
    space = pymunk.Space()
    space.gravity = (0, 10)

    ## Initialize the arms.
    arms = []
    # Arm 1
    arm1 = Arm(space, (250, 250))
    arm1.addJoint(100)
    arm1.addJoint(50)
    arm1.addJoint(50, True)
    ## Arm 2
    arm2 = Arm(space, (750, 250),2)
    arm2.addJoint(150)
    arm2.addJoint(100)
    arm2.addJoint(50, True)
    # Arm 3
    arm3 = Arm(space, (500, 50),3)
    arm3.addJoint(250)
    arm3.addJoint(150)
    arm3.addJoint(100, True)

    # List of arms.
    arms = [arm1, arm2, arm3]

    ## Initialize the polygon.
    ## Generate a random polygon. For now lets get the triangles working.
    polygon = Polygon(space, 0.8, [[150, 100], [250, 100], [250, 200]])

    ## Set the goal state.
    ## Goal state is common for all the agents.
    resources = {
        "Space": space,
        "Arms": arms,
        "Object": polygon,
        "Goal": goalState
    }

    return resources


## TODO
## Add an outer box that kills the run if the body hits the end.
def scoreFrame(polygon, goalState, scoreData=(100, 0.75)):
    ScoreForAngle = scoreData[0]
    ScoreForPosition = scoreData[1]
    body = polygon.body

    score = abs(body.angle - goalState[0])*ScoreForAngle
    score += abs(body.position[0] - goalState[1])*ScoreForPosition
    score += abs(body.position[1] - goalState[2])*ScoreForPosition

    ## Punish the agent for getting the polygon outside the bounds.
    if abs(body.position[0]) > 2000 or abs(body.position[1]) > 2000:
        score += 1000000

    return score

## Given the agent and the resources, the agnets plays the game.
## The function gives it couple of mins to achieve the goal state.
## The game is scored.

def playOne(agent, resource, scoringFunc , LowPassFilter=0.8, framesPerAgent=120*60, PHYSICS_FPS=25, DT=1/60.0, agentActive=10):
    ## Get the resources for the agent
    arms = resource["Arms"]
    space = resource["Space"]
    polygon = resource["Object"]
    goalState = resource["Goal"]

    ## Collision handler
    armData = dict()
    ## Set all the with colission enabled.
    for idx, arm in enumerate(arms):
        armData["Arm_" + str(idx+1)] = [arm, True]
    
    collision = space.add_collision_handler(40, 20) #hard coded these since by default the collision type of arm and polygon is set to 20 and 40 respectively.
    collision.begin = polygon.on_collision_arbiter_begin #arm is an object of class Arm1

    score = 0
    frameNumber = 0
    while frameNumber < framesPerAgent:

        collision.data["polygon"] = polygon.body # polygon is an object of Polygon
        collision.data["arms_data"] = armData # armData is a disctionary that contains the information about arms.

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
            rawOut = agent.forwardPass(inputVector)
            ## Use the agents output to manipulate the arms.
            k = 0
            for armIdx, arm in enumerate(arms):
                newRates = []
                for _ in range(len(arm.Objects)):
                    newRates.append(rawOut[k])
                    k+=1 
                ## Set the arm speeds
                arm.agentToPhysics(newRates, 2.5)

                ## Activate or deactivate the gripper.
                # if rawOut[k] > 0.0:
                #     armData["Arm_" + str(armIdx+1)][1] = True
                # else:
                #     armData["Arm_" + str(armIdx+1)][1] = False
                #     arm.dropPolygon()
                k += 1

        frameScore = scoringFunc(polygon, goalState)
        #print(frameScore)
        score = LowPassFilter*score + (1-LowPassFilter)*frameScore
        ## Render only some of the frames. Makes it more smoother.
        for _ in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))

        # polygon.draw(window)
        # draw(space, window, draw_options)
        # clock.tick(FPS)
        frameNumber += 1
    print("Loss", score)
    return score


if __name__ == "__main__":
    lAgent = Agent()
    lAgent.addLayer("Input", 61, None, False)
    lAgent.addLayer("H0", 512, Linear, False)
    lAgent.addLayer("H1", 256, Sigmoid, False)
    lAgent.addLayer("H2", 128, TanH, False)
    lAgent.addLayer("H3", 64, Sigmoid, False)
    lAgent.addLayer("Output", 12, None, True)

    goalState = (
        0.0, # Angle
        400, # X axis 
        400, # Y axis
    )
    resources = initResourcers(goalState)

    playOne(lAgent, resources, score1)