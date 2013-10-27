from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from util import read_demo_description

import modshogun as sg
import numpy as np
import numpy.random as rnd
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return gaussian_process(request)

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel', 'PolynomialKernel', 'LinearKernel'],
            'argument_default': 'GaussianKernel',
            'argument_explain': 'Your choice for the covariance function'
        },
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_default': '5',
            'argument_explain': 'The degree to use with the PolynomialKernel'
        },
        {
            'argument_type': 'decimal',
            'argument_label': 'Kernel Width',
            'argument_name': 'sigma',
            'argument_default': '2.0',
            'argument_explain': 'The sigma to use in the GaussianKernel'
        },
        {
            'argument_type': 'decimal',
            'argument_label': 'Noise Level',
            'argument_name': 'noise_level',
            'argument_default': '0.1',
            'argument_explain': 'The noise level of the training points'
        },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'TrainGP',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }
    ]
    properties = { 'title': 'Gaussian Process Regression',
                   'template': {'type': 'coordinate-2dims',
                                'mouse_click_enabled': 'left',
                                'coordinate_system': {'horizontal_axis': {'range': [-5, 5]},
                                                      'vertical_axis': {'range': [-5, 5]}},
                                'description': read_demo_description.read_description(__file__)},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Arguments',
                           'panel_property': arguments
                       },
                       {
                           'panel_name': 'toy_data',
                           'panel_label': 'Toy Data'
                       }]}
    return render_to_response("regression/gaussian_process.html",
                              properties, context_instance = RequestContext(request))

def gaussian_process(request):
    result = []
    try:
        arguments = _read_toy_data(request)
        result = _process(*arguments)
    except:
        raise ValueError("Argument Error")

    return HttpResponse(json.dumps(result))

def _read_toy_data(request):
    y_set = []
    x_set = []
    toy_data = json.loads(request.POST['point_set'])
    for pt in toy_data:
        y_set.append(float(pt["y"]))
        x_set.append(float(pt["x"]))
    noise_level = float(request.POST['noise_level'])
    domain = json.loads(request.POST['axis_domain'])
    
    labels = np.array(y_set, dtype = np.float64)
    num = len(x_set)
    if num == 0:
        raise Http404
    examples = np.zeros((1, num))
    for i in xrange(num):
        examples[0,i] = x_set[i]
    feat_train = sg.RealFeatures(examples)
    labels = sg.RegressionLabels(labels)
    kernel = get_kernel(request, feat_train)
    return (feat_train, labels, noise_level, kernel, domain)

def _process(feat_train, labels, noise_level, kernel, domain):
    n_dimensions = 1

    likelihood = sg.GaussianLikelihood()
    likelihood.set_sigma(noise_level)
    covar_parms = np.log([2])
    hyperparams = {'covar': covar_parms, 'lik': np.log([1])}

    # construct covariance function
    SECF = kernel
    covar = SECF
    zmean = sg.ZeroMean()
    inf = sg.ExactInferenceMethod(SECF, feat_train, zmean, labels, likelihood)

    # location of unispaced predictions
    x_test = np.array([np.linspace(domain['horizontal'][0],
                                   domain['horizontal'][1],
                                   feat_train.get_num_vectors())])
    feat_test = sg.RealFeatures(x_test)

    gp = sg.GaussianProcessRegression(inf)
    gp.train()
    
#    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_COV)
    covariance = gp.get_variance_vector(feat_test)
#    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_MEANS)
    predictions = gp.get_mean_vector(feat_test)

    result = []
    for i in xrange(len(feat_test.get_feature_matrix()[0])):
        result.append({'x': feat_test.get_feature_matrix()[0][i],
                       'y': predictions[i],
                       'range_upper': predictions[i]+2*np.sqrt(covariance[i]),
                       'range_lower': predictions[i]-2*np.sqrt(covariance[i])})
    return result
