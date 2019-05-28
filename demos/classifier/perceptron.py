from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from common.fetch_data import get_binary_features
from util import read_demo_description

import shogun as sg
import numpy as np
import json

arguments = [
    {
        'argument_type': 'decimal',
        'argument_name': 'rate',
        'argument_label': 'Learning Rate',
        'argument_default': '1',
        'argument_explain': 'Affects the weight update per iteration. Should be a value in (0,1]'},
    {
        'argument_type': 'decimal',
        'argument_name': 'bias',
        'argument_label': 'Bias',
        'argument_default' : '0',
        'argument_explain': 'A constant value independent of the input'},
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

properties = { 'title': 'Perceptron(binary)',
               'template': {'type': 'coordinate-2dims',
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'x1',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'x2',
                                                                    'range': [0, 1]}},
                            'description': read_demo_description.read_description(__file__),
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
                       'panel_label': 'Toy Data',
                       'panel_property': toy_data_arguments}]}

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
        rate = float(request.POST["rate"])
        bias = float(request.POST['bias'])
        z_value, z_label = classify_perceptron(sg.Perceptron, features, labels, rate, bias)
    except Exception as e:
        return HttpResponse(json.dumps({"status": e}))

    return HttpResponse(json.dumps({ 'status': 'ok',
                                     'domain': [np.min(z_value), np.max(z_value)],
                                     'z': z_value.tolist() }))

def classify_perceptron(classifier, features, labels, learn=1, bias=0):
    perceptron = classifier(features, labels)
    perceptron.set_learn_rate(learn)
    perceptron.set_max_iter(100)
    perceptron.set_bias(bias)
    perceptron.train()
    
    size = 100
    x1 = np.linspace(0, 1, size)
    y1 = np.linspace(0, 1, size)
    x, y = np.meshgrid(x1, y1)
    
    test = sg.RealFeatures(np.array((np.ravel(x), np.ravel(y))))
    
    outl = perceptron.apply(test).get_labels()
    outv = perceptron.apply(test).get_values()
    
    # Normalize output
    outv /= np.max(outv)
    
    z_value = outv.reshape((size, size))
    z_value = np.transpose(z_value)
    
    z_label = outl.reshape((size, size))
    z_label = np.transpose(z_label)
    z_label = z_label + np.random.rand(*z_label.shape) * 0.01
    
    return z_value, z_label
