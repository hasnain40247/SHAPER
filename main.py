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

Population = 50

## Agents is a list of tuples.
## Each touple has the agent and the score.
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

## Set details of the space.
space = pymunk.Space()
## Currently no gravity.
space.gravity = (0, 0)


## We dont render stuff when we train as rendering will slow things down.
def initResourcers():
    pass

def playOne(agents, resources):
    score = 0
    framNumber = 0
    while framNumber > FramesPerAgent:
        inputVector = []
        for arm in arms:
            lTempData = arm.physicsToAgent()
            inputVector.extend(lTempData["Angles"])
            inputVector.extend(lTempData["Rates"])
            inputVector.extend(lTempData["Positions"])
        inputVector = np.array(inputVector)
        rawOut = agent.forwardPass(inputVector)
        print("Out:", rawOut)
        ## Use the agents output to manimulate the arms.
        k = 0
        for arm in arms:
            newAngles = []
            for idx in range(len(arm.Objects)):
                newAngles.append((rawOut[k]+1)*(PI/2))
                k+=1 
            arm.setAngles(newAngles)

        ## Render only some of the frames. Makes it more smoother.
        for x in range(PHYSICS_FPS):
            space.step(DT/float(PHYSICS_FPS))

        
        for arm in arms:
            arm.getAngles()
        
        # polygon.draw(window)
        # draw(space, window, draw_options)
        #clock.tick(FPS)
        framNumber += 1
    return 

## Start the learning. 
while True:
    ## Generate a random polygon. For now lets get the triangles working.
    polygon = Polygon(space, (10,10), (0,0), [[150, 100], [250, 100], [250, 200]])

    ## Generate the polygon and the goal orientation. For now this is constant.
    ## Goal consists of the final poistion and angle of the body and the positions of the edges.
    goal = [
        0, #Angle
        150, 150, # pos1
        250, 150,  # pos2
        250, 250  # pos3
    ]

    pool =  Pool(Population)
    results = []
    for _ in range(Population):
        result = pool.apply_async(playOne)
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
