from django.http import HttpResponse, Http404
import numpy as np
import numpy.random as rnd
import json

def generate_classification_data(request):
    from modshogun import DataGenerator
    n = 40
    try:
        num_classes = int(float(request.POST['num_classes']))
        coverage = float(request.POST['overlapping'])
    except:
        raise Http404

    x = DataGenerator.generate_checkboard_data(num_classes, 2, n, coverage)
    toy_data = []
    for i in xrange(0,n-1):
        toy_data.append( {  'x': x[0, i],
                            'y': x[1, i], 
                            'label': x[2, i] })
    return HttpResponse(json.dumps(toy_data))

def generate_regression_data(request):
    xmin = -5
    xmax = 5
    n = 40
    x = (xmax-xmin-2)*rnd.rand(n)+xmin
    x.sort()
    #x = np.linspace(-5,5,n)
    C = 0 #offset
    b = 0
    amplitude = 1
    frequency = 1
    noise_level = 0.1
    try:
        amplitude = float(request.POST['amplitude'])
        frequency = float(request.POST['frequency'])
        noise_level = float(request.POST['noise_level'])
    except:
        raise Http404
    
    y = b*x + C + np.linspace(0,amplitude, len(x)) * np.sin(frequency * x)
    y += noise_level*rnd.randn(y.shape[0])
    
    toy_data = []
    for i in xrange(len(x)):
        toy_data.append( { 'x': x[i],
                           'y': y[i],
                           'label': '1'})
    return HttpResponse(json.dumps(toy_data))

def generate(request):
    if (request.POST['action'] and request.POST['action'] == 'classify'):
        print 'Calling'
        return generate_classification_data(request)
    else:
        return generate_regression_data(request)

