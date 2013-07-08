from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel

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
            'argument_name': 'degree',
            'argument_default': '5'
        },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'regress',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }
        ]
        
    properties = { 'title': 'Supported Vector Regression Demo',
                   'template': {'type': 'coordinate-2dims',
                                'heatmap': False,
                                'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                          'label': 'x-axis',
                                                                          'range': [0, 1]},
                                                      'vertical_axis': {'position': 'left',
                                                                        'label': 'y-axis',
                                                                        'range': [0, 1]}},
                                'mouse_click_enabled': 'left'},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Arguments',
                           'panel_property': arguments
                       },
                       {
                           'panel_name': 'toy_data',
                           'panel_label': 'toy data',
                       }]}
    return render_to_response("svr/index.html", properties, context_instance=RequestContext(request))
    
def point(request):
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
