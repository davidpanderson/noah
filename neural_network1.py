from scipy.optimize import minimize

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
    def __init__(self, nsl):
        self.layers = [neuron = [.5, False] for l in nsl for inti in range\
        (len(l))
        self.layers = [layer(layer) for layer in self.layers

    def run_network(inputs):
        for layer in self.layers:
            output = layer.run_layer(inputs)
            outputs.append(output)
            inputs = outputs
            return outputs

   def get_output(outputs, thresholds)
        for i in range(leng(outputs)):
            for t in thresholds:
                if outputs[i] > t:
                    current_fits.append(thresholds.index(t))
                    counter += 1
                if counter > 1:
                    real_outputs.append(False)
                else:
                    real_outputs.append(current_fits[0])
                counter = 0
        return real_outputs

    def test_network(inputs, expected_results, thresholds):
        counter = 0
        outputs = [self.run_network(input) for input in inputs]
        real_outputs = self.get_output(outputs, thresholds)
        for output in real_outputs:
            if output == True:
                counter += 1
        return counter        
        
    def train():
        net = minimize(cost, x0, method='Nelder-Mead', options={'xtol': 1\
        e-2, 'maxfev':1000, 'maxiter': 100000, 'disp': True})
        return net

