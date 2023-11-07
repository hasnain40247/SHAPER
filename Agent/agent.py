import numpy as np
from math import exp

## Activation functions
def Sigmoid(x):
    return 2*(1/(1+np.exp(-1*x))-0.5)

## Output is not always between -1 and 1
def ELU(x):
    y = np.where(x<=0, x, 0.1*x)
    return np.where(y>1,y,1)

def Linear(x):
    return x

def Normalize(x):
    return (x-x.min())/(x.max()-x.min())

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
    def addLayer(self, layerName, size, activation=Linear, output=False):
        if self.complete:
            print("Cannot resize a network once memory has been allocated. Delete and create a new agent.")
            return
        if len(self.layers) == 0:
            self.layers.append({"Name": layerName, "Size":size, "Activation": Linear})
        else:
            self.layers.append({"Name": layerName, "Size":size, "Activation": activation})
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

    def forwardPass (self, inputVector):
        if self.complete:
            out = np.matmul(inputVector, self.network[0])
            out = self.activation[0](out)
            for idx in range(1, len(self.network)):
                out = np.matmul(out, self.network[idx])
                out = self.activation[idx](out)
            return out
        else:
            print("Cnnot predict with an incomplete network.")
        return None
    
    ## Might be needed in the future.
    def matToVec(self):
        pass

    def vecToMat(self):
        pass


    def save(self):
        if self.complete:
            ## TODO implement me!!
            pass

    def load(self, path):
        if not self.complete:
            ## TODO Implement me!!
            pass
        
    ## Just to print the network in a nice way.
    def __repr__(self) -> str:
        out = ""
        for idx in range(len(self.layers)):
            out += "Layer: " + self.layers[idx]["Name"] + " Size: " +  str(self.layers[idx]["Size"]) + "\n"
        out += "Complete: " + str(self.complete) + "\n"
        out += "Length of Networks: " + str(len(self.network)) + "\n"
        out += "Length of Activations: " + str(len(self.activation)) + "\n"
        return out

    ## Mutate the agent
    ## Please check me out. Have some issues here.
    def mutate(self, eta=0.01):
        if not self.complete:
            return
        for idx in range(len(self.network)):
            matShape = self.network[idx].shape
            change = (np.random.rand(matShape[0],matShape[1])-0.5)*2*eta
            newMatrix = self.network[idx] + change
            self.network[idx]= newMatrix
            self.network[idx] = Normalize(self.network[idx])


## Just some testing code.
if __name__ == "__main__":
    ## Make an agegnt.
    a = Agent()

    ## Add all the layers as required.
    a.addLayer("Input", 28, None, False)
    #a.addLayer("H1", 150, Sigmoid, False)
    #a.addLayer("H2", 50, Sigmoid, False)
    a.addLayer("H3", 20, Sigmoid, False)
    a.addLayer("Output", 10, Sigmoid, True)

    ## Generate a random input.
    input = np.random.rand(1,28)
    #print(a)

    ## Get an output for the random input.
    out1 = a.forwardPass(input)
    
    a.mutate()
    
    out2 = a.forwardPass(input)
    print(out1)
    print(out2)