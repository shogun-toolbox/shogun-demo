from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from util import read_demo_description

import modshogun as sg
import numpy as np
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return regression(request)

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_label': 'Regression',
            'argument_name': 'regression',
            'argument_items': ['LeastSquaresRegression',
                               'LinearRidgeRegression',
                               'KernelRidgeRegression'],
            'argument_explain': 'Regression tool'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'sigma',
            'argument_default': '0.3',
            'argument_explain': 'For GaussianKernel (KernelRidgeRegression)'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'Tau',
            'argument_default': '5',
            'argument_explain': 'tau to use in the (Kernel)RidgeRegression'
        },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'regress',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }]

    toy_data_arguments = [
        {
            'problem_type': 'regression',
            }
        ]

        
    properties = { 'title': 'Regression',
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
                       }],
                    'data_sets' : ['boston_housing']
                       }
    return render_to_response("regression/regression.html",
                              properties,
                              context_instance=RequestContext(request))
    
def regression(request):
    try:
        domain = json.loads(request.POST['axis_domain'])        
        X = np.linspace(domain['horizontal'][0], domain['horizontal'][1], 100) 
        x = np.array([X])
        feat = sg.RealFeatures(x)

        arguments=_read_data(request)
        
        tool=request.POST['regression']
        if (tool == 'LeastSquaresRegression'):
            ls = _train_ls(*arguments)
            y = _apply_ls(feat, ls)
        
        elif (tool == 'LinearRidgeRegression'):
            lrr = _train_lrr(*arguments)
            y = _apply_lrr(feat, lrr)

        elif (tool=='KernelRidgeRegression'):
            krr, kernel, train =_train_krr(*arguments)
            y = _apply_krr(kernel, train, feat, krr)

        line_dot = []
        for i in xrange(len(X)):
            line_dot.append({'x' : X[i], 'y' : y[i]})
        return HttpResponse(json.dumps(line_dot))
    except:
        raise Http404
            
def _read_data(request):
    labels = []
    features = []
    data = json.loads(request.POST['point_set'])
    tau = float(request.POST['Tau'])
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
    
    sigma = float(request.POST["sigma"])
    kernel = sg.GaussianKernel(train, train, sigma)

    return (tau, lab, kernel, train)
                
def _train_krr(tau, lab, kernel, train):
    krr = sg.KernelRidgeRegression(tau, kernel, lab)
    krr.train(train)
    return krr, kernel, train

def _apply_krr(kernel, train, feat, krr):
    kernel.init(train, feat)
    y = np.array(krr.apply().get_labels(), dtype=np.float64)
    return y


def _train_ls(tau, lab, kernel, train):
    ls = sg.LeastSquaresRegression(train, lab)
    ls.train()
    return ls

def _apply_ls(feat, ls):
    y = np.array(ls.apply(feat).get_labels(), dtype=np.float64)
    return y

def _train_lrr(tau, lab, kernel, train):
    lrr = sg.LinearRidgeRegression(tau, train, lab)
    lrr.train()
    return lrr

def _apply_lrr(feat, lrr):
    y = np.array(lrr.apply(feat).get_labels(), dtype=np.float64)
    return y

