import mnist_loader
import numpy as np
import sknn
cou = 0
cou2 = 0
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
training_data = np.array(training_data)
validation_data = np.array(validatin_data)
network = Regressor(layers=
                    [Layer('Sigmoid', units=784),
                     Layer('Sigmoid', units = 30),
                     Layer('Sigmoid', units = 10)])
                 #   learning_rate=.01, n_iter=5)
network.fit([n_samples, training_data[0]], n_samples, training_data[1])
outputs = network.predict(n_samples2, validation_data[0])
for output in outputs:
    if validation_data[1][cou] == output:
        cou2 += 1
    cou += 1
print(cou2)
