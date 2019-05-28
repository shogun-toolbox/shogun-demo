from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from util import read_demo_description

import shogun as sg
import numpy as np
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return support_vector_regression(request)

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel', 'PolynomialKernel', 'LinearKernel' ],
            'argument_default': 'GaussianKernel',
            'argument_explain': '<i>Kernel</i> Function',
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'C',
            'argument_default': '1.2',
            'argument_explain': 'Penalty parameter of the error term'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'tube',
            'argument_default': '0.04',
            'argument_explain': 'Specifies the allowed deviation of the prediction from the actual value'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'sigma',
            'argument_default': '0.3',
            'argument_explain': 'The sigma to use in the GaussianKernel'
        },
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_default': '5',
            'argument_explain': 'The degree to use in the PolynomialKernel'
        },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'regress',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }
        ]
    toy_data_arguments = [
        {
            'problem_type': 'regression',
            }
        ]
        
    properties = { 'title': 'Supported Vector Regression',
                   'template': {'type': 'coordinate-2dims',
                                'heatmap': False,
                                'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                          'label': 'x-axis',
                                                                          'range': [0, 1]},
                                                      'vertical_axis': {'position': 'left',
                                                                        'label': 'y-axis',
                                                                        'range': [0, 1]}},
                                'mouse_click_enabled': 'left',
                                'description': read_demo_description.read_description(__file__)},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Arguments',
                           'panel_property': arguments
                       },
                       {
                           'panel_name': 'toy_data',
                           'panel_label': 'toy data',
                           'panel_property': toy_data_arguments
                       }]}
    return render_to_response("regression/support_vector_regression.html",
                              properties,
                              context_instance=RequestContext(request))
    
def support_vector_regression(request):
    try:
        arguments=_read_data(request)
        svm=_train_svr(*arguments)
        domain = json.loads(request.POST['axis_domain'])
        x=np.linspace(domain['horizontal'][0], domain['horizontal'][1], 100)
        y=np.array(svm.apply(sg.RealFeatures(np.array([x]))).get_labels(), dtype=np.float64)
        line_dot = []
        for i in xrange(len(x)):
            line_dot.append({'x' : x[i], 'y' : y[i]})
        return HttpResponse(json.dumps(line_dot))
    except:
        raise Http404
            
def _read_data(request):
    labels = []
    features = []
    data = json.loads(request.POST['point_set'])
    cost = float(request.POST['C'])
    tubeeps = float(request.POST['tube'])
    kernel_name = request.POST['kernel']
    for pt in data:
        labels.append(float(pt["y"]))
        features.append(float(pt["x"]))
    labels = np.array(labels, dtype=np.float64)
    num = len(features)
    if num == 0:
        raise TypeError
    examples = np.zeros((1,num))
    
    for i in xrange(num):
        examples[0,i] = features[i]
    
    lab = sg.RegressionLabels(labels)
    train = sg.RealFeatures(examples)
    kernel = get_kernel(request, train)
    return (cost, tubeeps, lab, kernel)
                
def _train_svr(cost, tubeeps, lab, kernel):
    svm = sg.LibSVR(cost, tubeeps, kernel, lab)
    svm.train()
    svm.set_epsilon(1e-2)
    return svm
