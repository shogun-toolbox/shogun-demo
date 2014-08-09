import numpy as np
import modshogun as sg

def classify_gp(features, labels, kernel, domain, lik, learn, scale, returnValues=True):
    mean = sg.ZeroMean()
    inf = sg.EPInferenceMethod(kernel, features, mean, labels, lik)
    inf.set_scale(scale)
    gp = sg.GaussianProcessBinaryClassification(inf)
    best_width=0.0
    best_param=0
    best_degree=0
    best_scale=0.0

    if learn == 'ML2':
        inf.set_scale(1)
        if kernel.get_name() == 'GaussianKernel':
            kernel.set_width(1)
        grad = sg.GradientEvaluation(gp, features, labels, sg.GradientCriterion(), False)
        grad.set_function(inf)
        grad_search = sg.GradientModelSelection(grad)
        best_combination = grad_search.select_model()
        best_combination.apply_to_machine(gp)
        try:
            best_width=sg.GaussianKernel.obtain_from_generic(inf.get_kernel()).get_width()
        except:
            pass
        best_scale = inf.get_scale()       
    gp.train()
   
    size = 50
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
    return x, y, z, best_width, best_param, best_scale
