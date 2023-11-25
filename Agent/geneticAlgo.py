import yaml
from agent import Agent

class GNN:
    def __init__(self,modelPath, totalPop=10, parents=2, lossFunc=None, max=True):
        if lossFunc == None or totalPop < 3 or parents < 2:
            print("Invalid data")
            raise Exception("Invalid initialization")        
        self.populationCount = totalPop
        self.parentsCount = parents
        self.direction = max
        self.loss = lossFunc

        yamlData = None
        with open(modelPath, "r") as stream:
            try:
                yamlData = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise Exception(exc)

        try:
            inputSize = yamlData["inputSize"]
            outputSize = yamlData["outputSize"]

            hiddenLayes = []
            for hData in yamlData["hiddenLayers"]:
                hiddenLayes.append(hData["size"])

            hiddelnLayerCount = len(hiddenLayes)
        except KeyError:
            return
        self.agents = [Agent(inputSize, outputSize, hiddelnLayerCount, hiddenLayes)]*self.populationCount

    def fit(self):
        pass

    def getPrediction(self, i,input):
        if i > self.populationCount-1:
            return "invalid"
        return self.agents[i].Predict(input)