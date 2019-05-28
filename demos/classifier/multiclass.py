from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from common.fetch_data import get_multi_features
from demos.classifier import svm
from util import read_demo_description

import shogun as sg
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
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'classify',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }]

toy_data_arguments = [
        {
            'problem_type': 'classification',
            'x_range': [0, 1],
            'y_range': [0, 1]
        }]

properties = { 'title': 'Multiclass Classifier',
               'template': {'type': 'coordinate-2dims',
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'x1',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'x2',
                                                                    'range': [0, 1]}},
                            'description': read_demo_description.read_description(__file__),
                            'heatmap': { 'contour': True },
                            'mouse_click_enabled': 'left',
                            'feature_number': 4},
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
def entrance(request):
    return render_to_response("classifier/multiclass.html",
                              properties,
                              context_instance=RequestContext(request))

def classify(request):
    C = json.loads(request.POST["C"])
    try:
        features, labels = get_multi_features(request)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    try:
        kernel = get_kernel(request, features)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    
    learn = "No"  
    values=[]

    try:
        domain = json.loads(request.POST['axis_domain'])
        x, y, z = svm.classify_svm(sg.GMNPSVM, features, labels, kernel, domain, learn, values, C, False)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

#    z = z + np.random.rand(*z.shape) * 0.01
	
    z_max = np.nanmax(z)
    z_min = np.nanmin(z)
    z_delta = 0.1*(np.nanmax(z)-np.nanmin(z))
    data = {"status": "ok",
            "domain": [z_min-z_delta, z_max+z_delta],
            "max": z_max+z_delta,
            "min": z_min-z_delta,
            "z": z.tolist()}

    return HttpResponse(json.dumps(data))

