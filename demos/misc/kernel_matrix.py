from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return kernel_matrix(request)

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
            'argument_items': [{'button_name': 'generate',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]},
        ]
    properties = { 'title': 'Kernel Matrix Visualization',
                   'template': {'type': 'coordinate-2dims',
                                'mouse_click_enabled': 'left',
                                'heatmap': { 'contour': True },
                                'coordinate_system': {'horizontal_axis': {'range':[-5.0, 5.0]},
                                                      'vertical_axis': {'range':[-4.0, 4.0]}}},
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
    return render_to_response("misc/kernel_matrix.html",
                              properties,
                              context_instance = RequestContext(request))

def kernel_matrix(request):
    result = []
    try:
        arguments = _read_toy_data(request)
        result = _process(*arguments)
    except:
        raise Http404

    return HttpResponse(json.dumps({'status': 'ok',
                                    'domain': [np.min(result), np.max(result)],
                                    'z': result}))

def _read_toy_data(request):
    y_set = []
    x_set = []
    data = json.loads(request.POST['point_set'])
    for pt in data:
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
