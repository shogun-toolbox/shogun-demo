from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from demos import dimred
from util import read_demo_description

import difflib
import shogun as sg
import numpy as np
import json

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'demo_switch',
            'argument_label': 'Feature Type',
            'argument_items': ['MIT_CBCL_faces_embedding',
                               'words_embedding',
                               'MNIST_digits_embedding',
                               'promoters_embedding',
                               'faces_embedding'],
            },
        {
            'argument_type': 'decimal',
            'argument_name': 'k',
            'argument_label': 'k',
            'argument_default': '20',
            'argument_explain': 'Number of neighbors to consider'
            },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'show'},
                               {'button_name': 'clear'}],
            }
        ]
    properties = {'title': 'Dimension Reduction',
                  'template': {'type': 'coordinate-2dims',
                               'mouse_click_enabled': 'none',
                               'description': read_demo_description.read_description(__file__)},
                  'panels':[
                      {
                          'panel_name': 'arguments',
                          'panel_label': 'Arguments',
                          'panel_property': arguments
                      }]}
                
    return render_to_response("dimred/tapkee.html",
                              properties,
                              context_instance = RequestContext(request))

def words(request):
    try:
        k = int(request.POST['k'])
    except:
        return HttpResponse(json.dumps({"status": "illegal k"}))

    if k<5 or k>dimred.N:
        raise ValueError("illegal k")

    converter = sg.KernelLocallyLinearEmbedding()
    converter.set_k(k)
    converter.set_target_dim(2)
    converter.parallel.set_num_threads(4)
        
    embedding = converter.embed_kernel(dimred.word_kernel).get_feature_matrix()
    
    data = {}
    data['data'] = [{'string':dimred.words[i],
                     'cx':embedding[0,i],
                     'cy':embedding[1,i]} for i in xrange(dimred.N)]
    return HttpResponse(json.dumps(data))

    
def promoters(request):
    features = sg.StringCharFeatures(dimred.strings,sg.DNA)
    kernel = sg.WeightedDegreeStringKernel(10)
    distance = sg.KernelDistance(1.0,kernel)
    distance.init(features,features)
    converter = sg.MultidimensionalScaling()
    converter.set_target_dim(2)
    embedding = converter.embed_distance(distance).get_feature_matrix()

    data = {}
    N = len(dimred.strings)
    data['data'] = [{'string':dimred.strings[i][:20],
                     'gc': float(dimred.strings[i].count('G') +
                                 dimred.strings[i].count('C'))/len(dimred.strings[i]), 
                     'cx':embedding[0,i],
                     'cy':embedding[1,i]} for i in xrange(N)]
    return HttpResponse(json.dumps(data))
