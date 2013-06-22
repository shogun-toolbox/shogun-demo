from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_label': 'Distance',
            'argument_name': 'distance',
            'argument_items': ['EuclideanDistance',
                             'ManhattanMetric',
                             'JensenMetric']},
        {
            'argument_type': 'integer',
            'argument_name': 'number_of_clusters',
            'argument_label': 'Number of Clusters (<500)',
            'argument_default': '2'},
        {
            'argument_type': 'button-group',
            'argument_items': ['cluster', 'clear']
        }]
    properties = { 'title': 'Clustering Demo',
                   'template': {'type': 'coordinate-2dims',
                                'coordinate_range': {'horizontal': [0 ,1],
                                                     'vertical': [0, 0.8]},
                                'horizontal_axis': {'position': 'bottom',
                                                    'label': 'X-axis'},
                                'vertical_axis': {'position': 'left',
                                                  'label': 'Y-axis'}},
                   'arguments': arguments}
    return render_to_response("clustering/index.html", properties, context_instance=RequestContext(request))

def cluster(request):
    try:
        arguments = _read_data(request)
        kmeans = _train_clustering(*arguments)
        centers = kmeans.get_cluster_centers()
        radi = kmeans.get_radiuses()
        result = {'circle': []}
        for i in xrange(arguments[3]): # arguments[3] is k
            result['circle'].append({'x': centers[0,i],
                                     'y': centers[1,i],
                                     'r': radi[i]})
        return HttpResponse(json.dumps(result))
    except:
        return HttpResponseNotFound()
    
def _read_data(request):
    k = int(request.POST['number_of_clusters'])
    if k > 500:
        raise TypeError
    positive = json.loads(request.POST['positive'])['points']
    negative = json.loads(request.POST['negative'])['points']
    distance_name = request.POST['distance']
        
    if len(positive) == 0 and len(negative) == 0:
        raise TypeError
    return (positive, negative, distance_name, k)
   
def _train_clustering(positive, negative, distance_name, k):
    labels = np.array([1]*len(positive) + [-1]*len(negative), dtype=np.float64)
    num_pos = len(positive)
    num_neg = len(negative)
    features = np.zeros((2, num_pos+num_neg))
    
    for i in xrange(num_pos):
        features[0, i] = positive[i]['x']
        features[1, i] = positive[i]['y']
         
    for i in xrange(num_neg):
        features[0, i+num_pos] = negative[i]['x']
        features[1, i+num_pos] = negative[i]['y']
                 
    lab = sg.BinaryLabels(labels)
    train = sg.RealFeatures(features)
             
    if distance_name == "EuclideanDistance":
        distance = sg.EuclideanDistance(train, train)
    elif distance_name == "ManhattanMetric":
        distance = sg.ManhattanMetric(train, train)
    elif distance_name == "JensenMetric":
        distance = sg.JensenMetric(train, train)
    else:
       raise TypeError
                  
    kmeans = sg.KMeans(k, distance)
    kmeans.train()

    return kmeans
