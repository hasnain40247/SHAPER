import numpy as np
from math import exp
import pymunk
import random
import os
from matplotlib import pyplot as plt

def TanH(x):
    return np.tanh(x)

## Activation functions
def Sigmoid(x):
    return 2*(1/(1+np.exp(-1*x))-0.5)

## Output is not always between -1 and 1
def ELU(x):
    y = np.where(x<=0, x, 0.1*x)
    return np.where(y>1,y,1)

def Linear(x):
    return x

def ReLu(x):
    return (x+abs(x))/2

def vectorize(mat):
    size = mat.shape[0] * mat.shape[1]
    return np.reshape(mat, size)

def vecToMat(vec, shape):
    return np.reshape(vec, shape)


class Agent:
    def __init__(self):
        ## We use the comple variable to make sure the network is well definied.
        ## Once the network is well definied we allocate the memory and initialize the weights.
        ## complete should be set to True for the network to be used. 
        self.complete = False
        ## This stores the list of matrices that represent the neural network.
        ## This will be initialized when self.complete is moved to True
        self.network = []
        ## Stores the list of activation functions. One per layer. 
        self.activation = []
        ## Store the structure of the network as follows: [{Name: A, Size: x, activation: y}...]
        self.layers = []


    ## Name is a string. 
    ## Size is an integer.
    ## Activation must be a function that takes a single float input and returns a float number.
    ## If output is set to true, we allocate the memory for the network. q  
    def addLayer(self, layerName, size, activation, output=False):
        if self.complete:
            print("Cannot resize a network once memory has been allocated. Delete and create a new agent.")
            return
        if len(self.layers) == 0 or activation == None:
            self.layers.append({"Name": layerName, "Size":size, "Activation": Linear, "Output": output})
        else:
            self.layers.append({"Name": layerName, "Size":size, "Activation": activation, "Output": output})
        if output:
            self._createnetwork()
        
    def _createnetwork(self):
        if len(self.layers) == 2:
            self.network = (np.random.rand(self.layers[0]["Size"],self.layers[1]["Size"])-0.5)*2
            self.activation.append(self.layers[1]["Activation"])
        else:
            for idx in range(len(self.layers)-1):
                self.network.append((np.array(np.random.rand(self.layers[idx]["Size"],self.layers[idx+1]["Size"]))-0.5)*2)
                self.activation.append(self.layers[idx]["Activation"])
        self.complete = True

    def forwardPass (self, inputVector, v=False):
        if self.complete:
            if v:
                print("Input:", inputVector.shape)
                print("Layer 1:", self.network[0].shape, self.activation[0].__name__)
            out = np.matmul(inputVector, self.network[0])
            out = self.activation[0](out)
            for idx in range(1, len(self.network)):
                if v: print("Layer" + str(idx) + ":", self.network[idx].shape, self.activation[idx].__name__)
                out = np.matmul(out, self.network[idx])
                out = self.activation[idx](out)
            if v:
                print(out.shape)
            return out
        else:
            print("Cnnot predict with an incomplete network.")
        return None
    
    ## Might be needed in the future.
    def matToVec(self):
        pass

    def vecToMat(self):
        pass

    def save(self, path):
        if self.complete:
            try:
                os.mkdir(path)
            except FileExistsError:
                print("Folder already exists")
                pass
            for idx in range(len(self.network)):
                filePath = os.path.join(path, "network_" + str(idx))
                np.save(filePath, self.network[idx])

    def load(self, path):
        if self.complete:
            for idx in range(len(self.network)):
                filePath = os.path.join(path, "network_" + str(idx) + ".npy")
                self.network[idx] = np.load(filePath)


    def normalize(self, x):
        for idx in range(len(self.network)):
            self.network[idx] = (self.network[idx] - np.min(self.network[idx]))/(np.max(self.network[idx]) - np.min(self.network[idx]))
    
    ## Adds randomness to the network and normalizes the values.
    def mutate(self, eta=0.01):
        for idx in range(len(self.network)):
            rand = (np.random.rand(*self.network[idx].shape)-0.5)*2*eta
            self.network[idx] = self.network[idx] + rand
            self.network[idx] = (self.network[idx] - np.min(self.network[idx]))/(np.max(self.network[idx]) - np.min(self.network[idx]))

    ## Just to print the network in a nice way.
    def __repr__(self) -> str:
        out = ""
        for idx in range(len(self.layers)):
            out += "Layer: " + self.layers[idx]["Name"] + " Size: " +  str(self.layers[idx]["Size"]) + "\n"
        out += "Complete: " + str(self.complete) + "\n"
        out += "Length of Networks: " + str(len(self.network)) + "\n"
        out += "Length of Activations: " + str(len(self.activation)) + "\n"
        return out


## Take two agents and returns a new agent that is the combination of both.
## Each matrix is considered as an alle. Each parent contributes half of its alle.
def crossover(agent1, agent2):
    ## Assuming that agent1 and agent2 are of same dimensions.

    ## Create a new agent.
    newAgent = Agent()
    for layerIdx in range(len(agent1.layers)):
        layerDetails = agent1.layers[layerIdx]
        newAgent.addLayer(layerDetails["Name"], layerDetails["Size"], layerDetails["Activation"], layerDetails["Output"])

    ## TODO FIX THIS PLEASE.
    ## Looks like while creating a new child we are missing something.
    numOfMatrices = len(agent1.network)
    for matIdx in range(numOfMatrices):
        shape = agent1.network[matIdx].shape
        agent1Vec = vectorize(agent1.network[matIdx])
        agent2Vec = vectorize(agent2.network[matIdx])

        newVector = []
        for idx in range(agent1Vec.shape[0]):
            if np.random.random() > 0.5:
               newVector.append(agent1Vec[idx])
            else:
                newVector.append(agent2Vec[idx])
        newVector=np.array(newVector)
        newMat = vecToMat(newVector, shape)
        newAgent.network[matIdx] = newMat

    return newAgent

## Take two agents and returns a new agent that is the combination of both.
## Just averages the values of the weights.
def crossoverAvg(agent1, agent2):
    ## Assuming that agent1 and agent2 are of same dimensions.

    ## Create a new agent.
    newAgent = Agent()
    for layerIdx in range(len(agent1.layers)):
        layerDetails = agent1.layers[layerIdx]
        newAgent.addLayer(layerDetails["Name"], layerDetails["Size"], layerDetails["Activation"], layerDetails["Output"])

    numOfMatrices = len(agent1.network)
    for matIdx in range(numOfMatrices):
        newAgent.network[matIdx] = (agent1.network[matIdx]+agent2.network[matIdx])/2

    return newAgent

## Just some testing code.
if __name__ == "__main__":
    ## Make an agegnt.
    a = Agent()

    ## Add all the layers as required.
    a.addLayer("Input", 28, None, False)
    a.addLayer("H1", 150, Sigmoid, False)
    a.addLayer("H2", 50, Sigmoid, False)
    a.addLayer("H3", 20, ReLu, False)
    a.addLayer("Output", 10, None, True)

    a.save("./modelTest")

    loaded = Agent()

    ## Add all the layers as required.
    loaded.addLayer("Input", 28, None, False)
    loaded.addLayer("H1", 150, Sigmoid, False)
    loaded.addLayer("H2", 50, Sigmoid, False)
    loaded.addLayer("H3", 20, ReLu, False)
    loaded.addLayer("Output", 10, None, True)

    loaded.load("./modelTest")

    print(loaded.network[0] == a.network[0])

    ## Generate a random input.
    input = np.random.rand(1,28)
    print(a)

    ## Get an output for the random input.
    out = a.forwardPass(input, True)
    print(out)