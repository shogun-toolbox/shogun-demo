from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import difflib
import demo
import modshogun as sg
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
            'argument_default': '20'
            
            },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'show'},
                               {'button_name': 'clear'}],
            }
        ]
    properties = {'title': 'Dimension Reduction',
                  'template': {'type': 'coordinate-2dims',
                               'mouse_click_enabled': 'none'},
                  'panels':[
                      {
                          'panel_name': 'arguments',
                          'panel_label': 'Arguments',
                          'panel_property': arguments
                      }]}
                
    return render_to_response("tapkee/index.html",
                              properties,
                              context_instance = RequestContext(request))

def words(request):
    try:
        k = int(request.POST['k'])
    except:
        return HttpResponse(json.dumps({"status": "illegal k"}))

    N = len(demo.words)
    if k<5 or k>N:
        raise ValueError("illegal k")
        
    converter = sg.KernelLocallyLinearEmbedding()
    converter.set_k(k)
    converter.set_target_dim(2)
    converter.parallel.set_num_threads(1)
    
    
    dist_matrix = np.zeros([N,N])
    for i in xrange(N):
        for j in xrange(i,N):
            s = difflib.SequenceMatcher(None,demo.words[i],demo.words[j])
            dist_matrix[i,j] = s.ratio()
    dist_matrix = 0.5*(dist_matrix+dist_matrix.T)
    word_kernel = sg.CustomKernel(dist_matrix)
        
    embedding = converter.embed_kernel(word_kernel).get_feature_matrix()

    data = {}
  
    data['data'] = [{'string':demo.words[i],
                     'cx':embedding[0,i],
                     'cy':embedding[1,i]} for i in xrange(N)]
    
    return HttpResponse(json.dumps(data))

    
def promoters(request):
    features = sg.StringCharFeatures(demo.strings,sg.DNA)
    kernel = sg.WeightedDegreeStringKernel(10)
    distance = sg.KernelDistance(1.0,kernel)
    distance.init(features,features)
    converter = sg.MultidimensionalScaling()
    converter.set_target_dim(2)
    embedding = converter.embed_distance(distance).get_feature_matrix()

    data = {}
    N = len(demo.strings)
    data['data'] = [{'string':demo.strings[i][:20],
                     'gc': float(demo.strings[i].count('G')+demo.strings[i].count('C'))/len(demo.strings[i]), 
                     'cx':embedding[0,i],
                     'cy':embedding[1,i]} for i in xrange(N)]
    return HttpResponse(json.dumps(data))

