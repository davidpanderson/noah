import numpy as np
class neuron():
    def __init__(self, b, w, i):
        self.bias = b    
        self.inputs = i
        if not w:
            for i in range(len(i)):
                self.weights.append(np.random.randn(
def create_network(layer_sizes):
    network = []
    layer = 0
    for layer_size in layer_sizes:
        if layer == 0:
            network[counter] = 
