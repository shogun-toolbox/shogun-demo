import numpy as np
import modshogun as sg

def classify_gp(features, labels, kernel, domain, lik, returnValues=True):
    mean = sg.ZeroMean()
    inf = sg.EPInferenceMethod(kernel, features, mean, labels, lik)
    gp = sg.GaussianProcessBinaryClassification(inf)
    gp.train()
   
    size = 100
    x1 = np.linspace(domain['horizontal'][0], domain['horizontal'][1], size)
    y1 = np.linspace(domain['vertical'][0], domain['vertical'][1], size)
    x, y = np.meshgrid(x1, y1)
    
    test = sg.RealFeatures(np.array((np.ravel(x), np.ravel(y))))

    if returnValues:
        out = gp.apply(test).get_values()
    else:
        out = gp.apply(test).get_labels()
    z = out.reshape((size, size))
    z = np.transpose(z)
    return x, y, z
