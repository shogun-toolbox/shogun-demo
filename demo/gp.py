from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import scipy as sp
import json

def entrance(request):
    return render_to_response("gp/index.html", context_instance = RequestContext(request))

def create_toy_data(request):
    xmin = -5
    xmax = 5
    x = sp.arange(xmin, xmax, (xmax-xmin)/100.0)
    C = 0 #offset
    b = 0
    amplitude = 1
    frequency = 1
    noise_level = 0.1
    try:
        amplitude = float(request.POST['amplitude'])
        frequency = float(request.POST['frequency'])
        noise_level = float(request.POST['noise_level'])
    except:
        raise Http404
    
    y = b*x + C + amplitude * sp.sin(frequency * x)
    y += noise_level * np.random.randn(y.shape[0])

    toy_data = { 'data': [] }
    for i in xrange(len(x)):
        toy_data['data'].append( { 'x': x[i], 'y': y[i]})
    
    return HttpResponse(json.dumps(toy_data))

def train(request):
    result = []
    try:
        arguments = _read_toy_data(request)
        result = _process(*arguments)
    except:
        return HttpResponseNotFound()

    return HttpResponse(json.dumps(result))

def _read_toy_data(request):
    y_set = []
    x_set = []
    toy_data = json.loads(request.POST['toy_data'])
    for pt in toy_data:
        y_set.append(float(pt["y"]))
        x_set.append(float(pt["x"]))
    kernel_width = float(request.POST['kernel_width'])
    return (x_set, y_set, kernel_width)

def _process(x_set, y_set, kernel_width):
    labels = np.array(y_set, dtype = np.float64)
    num = len(x_set)
    if num == 0:
        raise Http404
    examples = np.zeros((1, num))
    for i in xrange(num):
        examples[0,i] = x_set[i]
    feat_train = sg.RealFeatures(examples)
    labels = sg.RegressionLabels(labels)
    n_dimensions = 1

    likelihood = sg.GaussianLikelihood()
    covar_parms = sp.log([2])
    hyperparams = {'covar': covar_parms, 'lik': sp.log([1])}

    # construct covariance function
    SECF = sg.GaussianKernel(feat_train, feat_train, kernel_width)
    covar = SECF
    zmean = sg.ZeroMean()
    inf = sg.ExactInferenceMethod(SECF, feat_train, zmean, labels, likelihood)

    # location of unispaced predictions
    x_test = np.array([np.linspace(-5, 5, feat_train.get_num_vectors())])
    feat_test = sg.RealFeatures(x_test)

    gp = sg.GaussianProcessRegression(inf, feat_train, labels)
    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_COV)
    covariance = gp.apply_regression(feat_test)
    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_MEANS)
    predictions = gp.apply_regression(feat_test)

    result = []
    for i in xrange(len(feat_test.get_feature_matrix()[0])):
        result.append({'x': feat_test.get_feature_matrix()[0][i],
                       'y': predictions.get_labels()[i],
                       'range_upper': predictions.get_labels()[i]+3*np.sqrt(covariance.get_labels()[i]),
                       'range_lower': predictions.get_labels()[i]-3*np.sqrt(covariance.get_labels()[i])})
    return result
