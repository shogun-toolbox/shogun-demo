from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from common.fetch_data import get_binary_features
from demos.classifier import svm
from util import read_demo_description

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
            'argument_default': '1.2',
            'argument_explain': 'Regularization constant'},
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
            'argument_type': 'select',
            'argument_label': 'Learn parameters',
            'argument_name': 'learn',
            'argument_items': ['No', 'GridSearch'],
            'argument_explain': 'Learn parameters using model selection'},
        {
            'argument_type': 'select',
            'argument_class': 'hide',
            'argument_label': 'GridSearch values From:',
            'argument_name': 'polygrid1',
            'argument_items':['0','1','2','3','4'],
            'argument_explain': 'Range of values for learning degree of PolyKernel '},
        {
            'argument_type': 'select',
            'argument_class':'hide',
            'argument_label': 'To:',
            'argument_name': 'polygrid2',
            'argument_items':['1','2','3','4','5'],
            'argument_explain': 'Range of values for learning degree of PolyKernel '},
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

properties = { 'title': 'Binary Classification',
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
                   'data_sets' : ['diabetes']}

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
    value=[]
    try:
        features, labels = get_binary_features(request)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        kernel = get_kernel(request, features)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))    

    try:
        learn = request.POST["learn"]
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    
    if int(features.get_num_vectors()) > 100 and learn == "GridSearch":
        return HttpResponse(json.dumps({"status": ("Model Selection " 
            "allowed only for less than 100 samples due to computational costs")}))

    if kernel.get_name() == 'PolyKernel' and learn == "GridSearch":
        value.append(int(request.POST["polygrid1"]))
        value.append(int(request.POST["polygrid2"]))
        if value[1] <= value[0]:
            return HttpResponse(json.dumps({"status": "Bad values for degree"}))

    try:
        C = float(request.POST["C"])
        domain = json.loads(request.POST['axis_domain'])
        x, y, z = svm.classify_svm(sg.LibSVM, features, labels, kernel, domain, learn, value, C=C)
    except Exception as e:
        import traceback
        return HttpResponse(json.dumps({"status": repr(traceback.format_exc(0))}))

    return HttpResponse(json.dumps({ 'status': 'ok',
                                     'domain': [np.min(z), np.max(z)],
                                     'z': z.tolist() }))


