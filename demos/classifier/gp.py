from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from common.likelihood import get_likelihood
from common.fetch_data import get_binary_features
from demos.classifier import gaussian_process
from util import read_demo_description

import modshogun as sg
import numpy as np
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return classify(request)

arguments = [
        {
            'argument_type': 'select',
            'argument_label': 'Kernel Function',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel',
                               'LinearKernel',
                               'PolynomialKernel'],
            'argument_explain': 'Kernel Function'},
        {
            'argument_type': 'select',
            'argument_label': 'Likelihood model',
            'argument_name': 'likelihood',
            'argument_items':['LogitLikelihood',
                              'ProbitLikelihood'],
            'argument_explain':'Likelihood model'},
        {
            'argument_type': 'select',
            'argument_label': 'Learn parameters',
            'argument_name': 'learn',
            'argument_items':['No',
                              'ML2'],
            'argument_explain':'Learn parameters using model selection'},
        {
            'argument_type': 'decimal',
            'argument_name': 'sigma',
            'argument_label': 'Sigma',
            'argument_default' : '0.1',
            'argument_explain': 'The sigma to use in the GaussianKernel'},
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_label': 'Degree',
            'argument_default': '2',
            'argument_explain': 'The degree to use in the PolynomialKernel'},
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'classify',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }]

toy_data_arguments = [
        {
            'problem_type': 'classification',
            'disable_class_input': 'disabled',
            'x_range': [0, 1],
            'y_range': [0, 1]
        }]

properties = { 'title': 'Gaussian Process Binary Classification',
               'template': {'type': 'coordinate-2dims',
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'x1',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'x2',
                                                                    'range': [0, 1]}},
                            'heatmap': { 'contour': True },
                            'mouse_click_enabled': 'both',
                            'description': read_demo_description.read_description(__file__)},
                'panels': [
                    {
                        'panel_name': 'arguments',
                        'panel_label': 'Arguments',
                        'panel_property': arguments
                    },
                    {
                        'panel_name': 'toy_data',
                        'panel_label': 'Toy Data',
                        'panel_property': toy_data_arguments}],
                   'data_sets' : ['australian']}

def entrance(request):
    return render_to_response("classifier/gp.html",
                              properties,
                              context_instance=RequestContext(request))

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
        lik = get_likelihood(request)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    try:
        learn = request.POST["learn"]
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    try:
        domain = json.loads(request.POST['axis_domain'])
        x, y, z, width, param = gaussian_process.classify_gp(features, labels, kernel, domain, lik, learn)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    return HttpResponse(json.dumps({ 'status': 'ok',
                                     'best_width': float(width),
                                     'best_param': float(param),
                                     'domain': [np.min(z), np.max(z)],
                                     'z': z.tolist() }))

