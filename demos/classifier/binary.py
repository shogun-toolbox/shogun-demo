from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from common.fetch_data import get_binary_features
from demos.classifier import svm

import modshogun as sg
import numpy as np
import json

arguments = [
        {
            'argument_type': 'select',
            'argument_label': 'Kernel Function',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel',
                               'LinearKernel',
                               'PolynomialKernel']},
        {
            'argument_type': 'decimal',
            'argument_name': 'C',
            'argument_default': '1.2'},
        {
            'argument_type': 'decimal',
            'argument_name': 'sigma',
            'argument_label': 'Sigma',
            'argument_default' : '0.1'},
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_label': 'Degree',
            'argument_default': '2'},
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'classify',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }]
properties = { 'title': 'Binary Classification',
               'template': {'type': 'coordinate-2dims',
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'x1',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'x2',
                                                                    'range': [0, 1]}},
                            'heatmap': { 'contour': True },
                            'mouse_click_enabled': 'both'},
                'panels': [
                    {
                        'panel_name': 'arguments',
                        'panel_label': 'Arguments',
                        'panel_property': arguments
                    },
                    {
                        'panel_name': 'toy_data',
                        'panel_label': 'Toy Data'}]}

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return classify(request)

def entrance(request):
    return render_to_response("classifier/binary.html",
                              properties,
                              context_instance = RequestContext(request))
def classify(request):
    try:
        features, labels = get_binary_features(request)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        kernel = get_kernel(request, features)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        C = float(request.POST["C"])
        x, y, z = svm.classify_svm(sg.LibSVM, features, labels, kernel, domain, C=C)
    except Exception as e:
        import traceback
        return HttpResponse(json.dumps({"status": repr(traceback.format_exc())}))

    return HttpResponse(json.dumps({ 'status': 'ok',
                                     'domain': [np.min(z), np.max(z)],
                                     'z': z.tolist() }))


