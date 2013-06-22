from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel', 'PolynomialKernel', 'LinearKernel' ],
            'argument_default': 'GaussianKernel'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'C',
            'argument_default': '1.2'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'tube',
            'argument_default': '0.04'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'sigma',
            'argument_default': '0.3'
        },
        {
            'argument_type': 'integer',
            'argument_name': 'd',
            'argument_default': '5'
        },
        {
            'argument_type': 'button-group',
            'argument_items': ['regress', 'clear']
        }
        ]
        
    properties = { 'title': 'Supported Vector Regression Demo',
                   'template': {'type': 'coordinate-2dims',
                                'coordinate_range': {'horizontal': [0, 1],
                                                     'vertical': [0, 0.8]},
                                'horizontal_axis': {'position': 'bottom',
                                                    'label': 'x-axis'},
                                'vertical_axis': {'position': 'left',
                                                    'label': 'y-axis'}},
                   'arguments': arguments }
    return render_to_response("svr/index.html", properties, context_instance=RequestContext(request))
    
def point(request):
    try:
        arguments=_read_data(request)
        svm=_train_svr(*arguments)
        x=np.linspace(0, 1, 100)
        y=np.array(svm.apply(sg.RealFeatures(np.array([x]))).get_labels(), dtype=np.float64)
        line_dot = []
        for i in xrange(len(x)):
            line_dot.append({'x_value' : x[i], 'y_value' : y[i]})
        return HttpResponse(json.dumps(line_dot))
    except:
        return HttpResponseNotFound()
            
def _read_data(request):
    labels = []
    features = []
    data = json.loads(request.POST['data'])
    cost = float(request.POST['C'])
    tubeeps = float(request.POST['tube'])
    degree = int(request.POST['d'])
    width = float(request.POST['sigma'])
    kernel_name = request.POST['kernel']
    for pt in data["points"]:
        labels.append(float(pt["y"]))
        features.append(float(pt["x"]))
    return (cost, tubeeps, degree, width, kernel_name, labels, features)
                
def _train_svr(cost, tubeeps, degree, width, kernel_name, labels, features):
    labels = np.array(labels, dtype=np.float64)
    num = len(features)
    if num == 0:
        raise TypeError
    examples = np.zeros((1,num))
                
    for i in xrange(num):
        examples[0,i] = features[i]
                    
    lab = sg.RegressionLabels(labels)
    train = sg.RealFeatures(examples)
                
    if kernel_name == "LinearKernel":
        gk = sg.LinearKernel(train, train)
        gk.set_normalizer(sg.IdentityKernelNormalizer())
    elif kernel_name == "PolynomialKernel":
        gk = sg.PolyKernel(train, train, degree, True)
        gk.set_normalizer(sg.IdentityKernelNormalizer())
    elif kernel_name == "GaussianKernel":
        gk = sg.GaussianKernel(train, train, width)
    else:
        raise TypeError
                    
    svm = sg.LibSVR(cost, tubeeps, gk, lab)
    svm.train()
    svm.set_epsilon(1e-2)
    return svm
