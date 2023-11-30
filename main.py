from Agent.agent import *
from Physics.polygon import *
from Physics.arm import *
from utils import *
from random import sample

PopulationCount = 5
ParentsCount = 2
ChildrenCount = PopulationCount-ParentsCount

SaveTimePeriod = 25

## Setup global variables
Resources = []
Agents = []
for _ in range(PopulationCount):
    lAgent = Agent()
    lAgent.addLayer("Input", 61, None, False)
    lAgent.addLayer("H0", 512, Linear, False)
    lAgent.addLayer("H1", 256, Sigmoid, False)
    lAgent.addLayer("H2", 128, TanH, False)
    lAgent.addLayer("H3", 64, Sigmoid, False)
    lAgent.addLayer("Output", 12, None, True)

    Agents.append([lAgent, 0.0])

generationNumber = 0

while True:
    goalState = (
        0.0, # Angle
        400, # X axis 
        400, # Y axis
    )

    for _ in range(PopulationCount):
        Resources.append(initResourcers(goalState))

    for idx in range(PopulationCount):
        score = playOne(Agents[idx][0], Resources[idx], score1)
        Agents[idx][1] = score

    Agents.sort(key=lambda x:x[1])

    print("\nLoss for generation ", generationNumber+1, end=" : ")
    for idx in range(ParentsCount):
        print(Agents[idx][1], end=", ")

    ## Save the  best every generation
    if generationNumber%SaveTimePeriod == 0:
        Agents[-1][0].save("Test_" + str(generationNumber+1))

    Parents = Agents[:ParentsCount]
    print("\nLoss for generation ", generationNumber+1, end=" : ")
    for idx in range(ParentsCount):
        print(Parents[idx][1], end=", ")

    Childeren = []

    for idx in range(ChildrenCount):
        matingParents = sample(Parents, 2)
        matingParents = matingParents[0][0], matingParents[1][0]
        newChild = crossover(*matingParents)
        newChild.mutate()
        Childeren.append([newChild, 0.0])

    Agents = []
    Resources = []

    for idx in range(ChildrenCount):
        Childeren[idx][1] = 0.0
        Agents.append(Childeren[idx])

    for idx in range(ParentsCount):
        Parents[idx][1] = 0.0
        Agents.append(Parents[idx])    
    generationNumber+=1
        