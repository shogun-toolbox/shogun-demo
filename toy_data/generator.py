from django.http import HttpResponse, Http404
import numpy as np
import numpy.random as rnd
import json

def generate(request):
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
        toy_data.append( { 'x': x[i], 'y': y[i]})
        
    return HttpResponse(json.dumps(toy_data))
