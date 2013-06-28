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
            'argument_items': ['Draw', 'Clear']},
        ]
    properties = { 'title': 'Kernel Matrix Visualization',
                   'template': {'type': 'coordinate-2dims',
                                'heatmap': True,
                                'coordinate_range': { 'horizontal': [-5.0, 5.0],
                                                      'vertical': [-4.0, 4.0] }},
                   'panels': [
                        {
                            'panel_name': 'arguments',
                            'panel_label': 'Arguments'
                        },
                        {
                            'panel_name': 'toy_data_generator',
                            'panel_label': 'Toy Data'
                        }],
                   'arguments': arguments}
    return render_to_response("kernel_matrix/index.html",
                              properties,
                              context_instance = RequestContext(request))

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
