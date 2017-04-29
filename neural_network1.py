import numpy as np
class neuron():
    def __init__(self, b, w, i):
        self.bias = b    
        self.inputs = i
        if not w:
            self.weights = [numpy.random.randn() for inti in range(len(i))]
    def sigmoid():
        1.0/(1.0 + np.exp(-(.np..dot(self.weights, self.inputs) + self.biases)))
        
class layer():
    def __init__(self, neurons):
        self.neurons = neurons
    def run_layer():
        self.outputs = [n.sigmoid() for n in self.neurons
        return self.outputs

class network():
    def __init__(inputs, self, nsl):
        self.layers = [neuron = [.5, False] for l in nsl for inti in range\
        (len(l))
                
        
