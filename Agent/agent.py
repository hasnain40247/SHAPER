import numpy as np
import os, sys
import random, copy


## Agent is the base class for all the entities in the the game. All NPC are based on this class.
## As the Agents are build such that their internal weighs can be altered during the learning process we have access to the network variable.
## All other variables are internal and will not be changed once instantiated.
class Agent():
    '''
    Initializes the Agent with random weights before being trained.
    '''
    def __init__(self, inputSize=None, outputSize=None, hiddenLayers=0, hiddenLayersShape=[], activationFuncs=[]):
        ## All weights are by default of type float64. This will take a lot of memory but it is better for precission.
        if inputSize==None or outputSize==None or (len(hiddenLayersShape) != hiddenLayers):
            self.network = None
            self.hiddenLayers = -1
            return

        self.savedWeights = None
        self.network = None
        self.hiddenLayers = hiddenLayers
        self.activationFuncList = []
        if hiddenLayers == 0:
            self.network = ([np.random.rand(inputSize,outputSize)]-0.5)*2
        else:
            self.network = []
            self.network.append((np.array([np.random.rand(inputSize,hiddenLayersShape[0])])-0.5)*2)
            for idx in range(hiddenLayers-1):
                self.network.append((np.array([np.random.rand(hiddenLayersShape[idx],hiddenLayersShape[idx+1])])-0.5)*2)
            self.network.append((np.array([np.random.rand(hiddenLayersShape[hiddenLayers-1],outputSize)])-0.5)*2)
        if len(activationFuncs) == 0:
            self.activationFuncList = [lambda x:x]*self.hiddenLayers+1
        else:
            for idx in range(self.hiddenLayers+1):
                #### Add checks to see if the functions are applicable to the the list of values
                self.activationFuncList.append(activationFuncs[idx])

    ## Given an input matrix of size (n, inputSize) gives an output of shape (outputShape, n)
    ## n is the number of inputs. Can be called on a single or multiple inputs at once.
    def Predict(self, inputMatrix):
        output = inputMatrix
        for idx in range(len(self.network)):
            output = np.matmul(output, self.network[idx])
            output = self.activationFuncList[idx](output)
        return output[0]
    
    def Mutate(self, m=10):
        for idx in range(len(self.network)):
            self.network[idx] = (mutation(self.network[idx], m))    


    ## Needs work
    def Print(self, f=sys.stdout):
        if f == sys.stdout:
            for idx in range(len(self.network)):
                print("Network", idx+1, file=f)
                print(self.network[idx], file=f)
                print("", file=f)
        elif type(f) == "str":
            np.savez(f, *self.network)                

    ## When we save we roll the entire list of matices into a single matrix of size (input*output)
    ## Doing so we will loose the actual internal weights but will allow us to reload it and use it for predictions.
    def Save(self, prefix="", postfix=""):
        self.savedWeights = self.network[0]
        for idx in range(1, len(self.network)):
            self.savedWeights = np.matmul(self.savedWeights, self.network[idx])
        fileName = prefix + "Agent" + postfix + ".npz"
        filePath = os.path.join("./persistedAgents/",fileName)
        np.save(filePath, self.savedWeights)

    ## Loads data from the file
    ## Once loaded the self.network and self.savedWeights are not gonna be consistent
    def Load(self, filePath):
        data = None
        if not filePath.endswith(".npy"):
            filePath += ".npy"
        try:
            data = np.load(filePath)
        except (FileNotFoundError, OSError):
            print("File not found.")
            return -1
        except Exception as e:
            print("Error: ", e)
            return -1
        self.savedWeights = data
        return data

    def PredictLoaded (self, inputMatrix):
        return np.matmul(inputMatrix, self.savedWeights)
    
## NSFW
## Not for your eyes. 8===D
def Crossover(agent1, agent2, cxType="Single"):
    ## Asuming that the shapes are the same.. If not this function will fail.
    match cxType:
        case "Single":
            return CrossoverSingle(agent1, agent2)
        case "Multiple":
            return CrossoverMultiple(agent1, agent2)
        case _:
            ## No crossover at all. Onle depends on mutation. Basically the best survie and rely on mutations.
            return agent1

## Very simple. But, can result iin children being the same as parent in some cases.
## This is fixed as all kinds have some mutation
def CrossoverSingle(agent1, agent2):
    lNewAgent = copy.deepcopy(agent1)
    crossoverPoint = random.randrange(len(agent1.network))
    for networkIdx in range(len(lNewAgent.network)):
        if networkIdx < crossoverPoint:
            lNewAgent.network[networkIdx] = agent1.network[networkIdx]
        else:
            lNewAgent.network[networkIdx] = agent2.network[networkIdx]
    return lNewAgent

## Very simple. But, can result iin children being the same as parent in some cases.
## This is fixed as all kinds have some mutation. ## Not yet done i gueess
def CrossoverMultiple(agent1, agent2, crossoverCount=2):
    if crossoverCount == 0:
        return agent1
    elif crossoverCount == 1:
        return CrossoverSingle(agent1,agent2)
    else:
        lNewAgent = copy.deepcopy(agent1)
        crossoverPoints = random.sample(list(range(len(agent1.network))), crossoverCount)
        for networkIdx in range(len(lNewAgent.network)):
            if networkIdx in crossoverPoints:
                lNewAgent.network[networkIdx] = agent1.network[networkIdx]
            else:
                lNewAgent.network[networkIdx] = agent2.network[networkIdx]
        return lNewAgent


## Converts data from [-1,1] to [0,1]
def Normalize(lTempData):
    ratio = 2/(np.max(lTempData)-np.min(lTempData)) 
    shift = (np.max(lTempData)+np.min(lTempData))/2
    return (lTempData - shift)*ratio

## Output is between -1 and 1
## Sigmoid has been modified to give value bewteen -1 and 1
def Sigmoid(x):
    return 2*(1/(1+np.exp(-1*x))-0.5)

## Output is not always between -1 and 1
def ELU(x):
    y = np.where(x<=0, x, 0.1*x)
    return np.where(y>1,y,1)

## takes a NP array as input and adds some random variation to it. 
## The randomness is in the range (-0.1 to 0.1)*m. m is the mutation rate between 0 and 100
def mutation(npArray, m=10):
    if len(npArray.shape) != 2:
        return npArray
    lTempData = (npArray + np.random.rand(npArray.shape[0],npArray.shape[1])*(m/100))
    lTempData = (lTempData-np.min(lTempData))/(np.max(lTempData)-np.min(lTempData))
    return lTempData
    
def main():
    TestAgent = Agent(
        24+6+1+2+1, # corners + current anglels for two arms + rotation rate + ver/horiz speed + goal slope
        8, # 2*4 two arms and 3 angles and grabby
        5, 
        [150,100,50,25,12],
        [Sigmoid]*8
    )
    #print(TestAgent.network)

    import time
    avgTime = 0
    totalCases = 100
    for i in range(totalCases):
        inputData = np.random.rand(1,34)
        s = time.time()
        output = TestAgent.Predict(inputData)
        avgTime += time.time() - s
    print("Avg time: ", avgTime/totalCases)

    print("Input", inputData.shape)
    print("Output", output.shape, output)

if __name__ == "__main__":
    main()