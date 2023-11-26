import pymunk
import pygame
from random import sample
import pymunk.pygame_util
from Agent.Agent2 import *
from Physics.arm import *
from Physics.arm2 import *
from Physics.polygon import *
from Physics.utils import *
from multiprocessing import Pool

PHYSICS_FPS = 25

Population = 5
LowPassFilter = 0.8

ScoreForAngle = 0.8
ScoreForPosition = 0.75

## Agents is a list of tuples.
## Each touple has the agent and the score. Need to change the inputs and outputs.
Agents = []   
for _ in range(Population):
    lAgent = Agent()
    lAgent.addLayer("Input", 54, None, False)
    lAgent.addLayer("H1", 256, Sigmoid, False)
    lAgent.addLayer("H2", 128, Sigmoid, False)
    lAgent.addLayer("H3", 64, Sigmoid, False)
    lAgent.addLayer("Output", 9, None, True)

    Agents.append((lAgent, 0.0))

## Top percentage of the population will be used as parents and 1-TopPic will be the children.
TopPic = 0.1
ParentsCount = TopPic*Population
ChildrenCount = Population-ParentsCount

FramesPerAgent = 60*120 ## 2 mins of real timee if rendered.


## We dont render stuff when we train as rendering will slow things down.
def initResourcers(goalState):
    ## Initialize the space.
    space = pymunk.Space()
    space.gravity = (0, 0)

    ## Initialize the arms.
    arms = []
    # Arm 1
    arm1 = Arm1(space, (250, 250))
    arm1.addJoint(100)
    arm1.addJoint(50)
    arm1.addJoint(50, True)
    ## Arm 2
    arm2 = Arm1(space, (750, 250),2)
    arm2.addJoint(150)
    arm2.addJoint(100)
    arm2.addJoint(50, True)
    # Arm 3
    arm3 = Arm1(space, (500, 50),3)
    arm3.addJoint(250)
    arm3.addJoint(150)
    arm3.addJoint(100, True)

    # List of arms.
    arms = [arm1, arm2, arm3]

    ## Initialize the polygon.
    ## Generate a random polygon. For now lets get the triangles working.
    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

    ## Set the goal state.
    ## Goal state is common for all the agents.
    resources = {
        "Space": space,
        "Arms": arms,
        "Object": polygon,
        "Goal": goalState
    }

    return resources

def scoreFrame(polygon, goalState):
    body = polygon.body

    score = (body.angle - goalState[0])*ScoreForAngle
    score += abs(body.position[0] - goalState[1])*ScoreForPosition
    score += abs(body.position[1] - goalState[2])*ScoreForPosition

    return score


def playOne(agent, resource):
    ## Get the resources for the agent
    arms = resource["Arms"]
    space = resource["Space"]
    polygon = resource["Object"]
    goalState = resource["Goal"]

    score = 0
    framNumber = 0
    while framNumber > FramesPerAgent:
        inputVector = []
        ## Input involving the arms.
        for arm in arms:
            lTempData = arm.physicsToAgent()
            inputVector.extend(lTempData["Angles"])
            inputVector.extend(lTempData["Rates"])
            inputVector.extend(lTempData["Positions"])
        
        ## Input involving the polygon.
        body = polygon.body
        polygonData = [body.position[0], body.position[1]]
        inputVector.extend(polygonData)
        
        ## Input regarding the goal.
        inputVector.extend(goalState)

        inputVector = np.array(inputVector)
        print("Input vector shape", inputVector.shape)

        ## Get the prediction from the agent.
        rawOut = agent.forwardPass(inputVector)
        ## Use the agents output to manipulate the arms.
        k = 0
        for arm in arms:
            newAngles = []
            for _ in range(len(arm.Objects)):
                newAngles.append((rawOut[k]+1)*(PI/2))
                k+=1 
            arm.setAngles(newAngles)

        ## Render only some of the frames. Makes it more smoother.
        for _ in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))
        
        ## GetAngles updates the angles of the arm based on the current arm location.
        for arm in arms:
            arm.getAngles()
        
        frameScore = scoreFrame(polygon, goalState)
        score = LowPassFilter*score + (1-LowPassFilter)*frameScore
        
        # polygon.draw(window)
        # draw(space, window, draw_options)
        #clock.tick(FPS)
        framNumber += 1
    return 

## Start the learning. 
while True:   
    ## Generate the polygon and the goal orientation. For now this is constant.
    ## Goal consists of the final poistion and angle of the body and the positions of the edges.
    goal = [
        0, #Angle
        150, 150, # poosition of the body
    ]

    ## Make it a tuple as it needs to be hashable.
    goal = tuple(goal)

    ## Generate the resources for each agent to play the game.
    resources = []
    for _ in range(len(Agents)):
        resources.append(initResourcers(goal))


    pool =  Pool(processes=Population)
    results = []
    for idx in range(Population):
        result = pool.apply_async(playOne, args=(Agents[idx], resources[idx],))
        results.append(result)
    [result.wait() for result in results]
    pool.join()
    pool.close()

    ## Give each of the some time to try and reach the goal state.
    ## Calculate the score for each agent

    ## Sort the agents by the scores and then generate the children.
    Agents.sort(key=lambda x: x[1])
    ## Replace the older generation with the newer generation.
    parents = Agents[:ParentsCount]

    ## Print the scores of the parents
    print("Top players: ",list(map(lambda x: x[1], parents)))

    for pIdx in range(len(parents)):
        parents[pIdx][1] = 0.0

    newChildren = []
    for _ in range(ChildrenCount):
        p1, p2 = sample(parents, 2)
        ## Choose two random parents
        newChild = crossover(p1, p2)
        newChild.mutate(eta=0.001)
        ## Mutate it and add it to the children's list
        newChildren.append((newChild ,0.0))

    Agents = newChildren+parents

    ## Break only if battery dies but before that save the weights...
    break
