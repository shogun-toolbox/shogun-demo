from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import scipy as sp
import json

def entrance(request):
    arguments = [
        {
            'argument_type': 'decimal',
            'argument_name': 'frequency',
            'argument_label': 'Sine Freq.',
            'argument_default': '1.0'},
        {
            'argument_type': 'decimal',
            'argument_name': 'amplitude',
            'argument_label': 'Amplitude',
            'argument_default': '1.0'},
        {
            'argument_type': 'decimal',
            'argument_name': 'noise_level',
            'argument_label': 'Noise Level',
            'argument_default': '0.3'},
        {
            'argument_type': 'select',
            'argument_label': 'Kernel Function',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel', 'PolynomialKernel', 'LinearKernel'],
            'argument_default': 'GaussianKernel'},
        {
            'argument_type': 'decimal',
            'argument_label': 'Kernel Width',
            'argument_name': 'kernel_width',
            'argument_default': '0.3'},
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_default': '5'},
        {
            'argument_type': 'button-group',
            'argument_items': ['CreateToyData', 'Draw', 'Clear']},
        {
            'argument_type': 'div',
            'argument_label': 'Legend',
            'argument_id': 'legend'}
        ]
    properties = { 'title': 'Kernel Matrix Visualization',
                   'template': {'type': 'coordinate-2dims',
                                'coordinate_range': { 'horizontal': [-5.0, 5.0],
                                                      'vertical': [-4.0, 4.0] }},
                   'arguments': arguments }
    return render_to_response("kernel_matrix/index.html",
                              properties,
                              context_instance = RequestContext(request))

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

def generate_matrix(request):
    result = []
    try:
        arguments = _read_toy_data(request)
        result = _process(*arguments)
    except:
        import traceback
        print traceback.format_exc()
        raise Http404

    return HttpResponse(json.dumps(result))

def _read_toy_data(request):
    y_set = []
    x_set = []
    toy_data = json.loads(request.POST['toy_data'])
    for pt in toy_data:
        y_set.append(float(pt["y"]))
        x_set.append(float(pt["x"]))
    kernel_width = float(request.POST['kernel_width'])
    degree = int(request.POST['degree'])
    kernel_name = request.POST['kernel']
    return (x_set, y_set, kernel_width, kernel_name, degree)

def _process(x1_set, x2_set, kernel_width, kernel_name, degree):
    num = len(x1_set)
    if num == 0:
        raise Http404
    examples = np.zeros((2, num))
    for i in xrange(num):
        examples[0,i] = x1_set[i]
        examples[1,i] = x2_set[i]
    feat_train = sg.RealFeatures(examples)

    # construct covariance function
    if kernel_name == "LinearKernel":
        kernel = sg.LinearKernel(feat_train, feat_train)
    elif kernel_name == "PolynomialKernel":
        kernel = sg.PolyKernel(feat_train, feat_train, degree, True)
    elif kernel_name == "GaussianKernel":
        kernel = sg.GaussianKernel(feat_train, feat_train, kernel_width)
    kernel_matrix=kernel.get_kernel_matrix()
    return kernel_matrix.tolist()
