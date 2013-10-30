from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from util import read_demo_description

import modshogun as sg
import numpy as np
import json

arguments = [
    {
        'argument_type': 'select',
        'argument_label': 'Distance Metric',
        'argument_name': 'distance',
        'argument_items': ['EuclideanDistance',
                           'ManhattanMetric',
                           'JensenMetric']
    },
    {
        'argument_type': 'integer',
        'argument_name': 'number_of_clusters',
        'argument_label': 'Number of Clusters (<500)',
        'argument_default': '2'
    },
    {
        'argument_type': 'button-group',
        'argument_items': [{'button_name': 'cluster',
                            'button_type': 'json_up_down_load'
                           },
                           {'button_name': 'clear'}]
    }]

toy_data_arguments = [
        {
            'problem_type': 'classification',
            'x_range': [0, 1],
            'y_range': [0, 1]
        }]

properties = { 'title': 'KMeans',
               'template': {'type': 'coordinate-2dims',
                            'feature': 'binary',
                            'coordinate_range': {'horizontal': [0, 1],
                                                 'vertical': [0, 0.8]},
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'X-axis',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'Y-axis',
                                                                    'range': [0, 1]}},
                            'description': read_demo_description.read_description(__file__),
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
                        'panel_property': toy_data_arguments}],
                   'data_sets' : ['australian']}

def entrance(request):
    return render_to_response("clustering/kmeans.html", properties, context_instance=RequestContext(request))

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return kmeans(request)

def kmeans(request):
    try:
        arguments = _read_data(request)
        kmeans = _train_clustering(*arguments)
        centers = kmeans.get_cluster_centers()
        radi = kmeans.get_radiuses()
        result = {'circle': []}
        for i in xrange(arguments[2]): # arguments[3] is k
            result['circle'].append({'x': centers[0,i],
                                     'y': centers[1,i],
                                     'r': radi[i]})
        return HttpResponse(json.dumps(result))
    except:
        import traceback
        print traceback.format_exc()
        return HttpResponseNotFound()
    
def _read_data(request):
    k = int(request.POST['number_of_clusters'])
    if k > 500:
        raise TypeError
    point_set = json.loads(request.POST['point_set'])
    distance_name = request.POST['distance']

    if len(point_set) == 0:
        raise TypeError
    return (point_set, distance_name, k)
   
def _train_clustering(point_set, distance_name, k):
    labels = np.array([0]*len(point_set))
    features = np.zeros((2, len(point_set)))

    for i in xrange(len(point_set)):
        features[0, i] = point_set[i]['x']
        features[1, i] = point_set[i]['y']
        labels[i] = point_set[i]['label']

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
