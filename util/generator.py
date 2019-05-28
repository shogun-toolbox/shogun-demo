from django.http import HttpResponse, Http404
import numpy as np
import numpy.random as rnd
import json

def generate_checkboard_data(request):
    from shogun import DataGenerator
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

def generate_gmm_classification_data(request):
    from shogun import GMM, Math

    num_classes = int(request.POST['num_classes'])
    gmm = GMM(num_classes)
    total = 40
    rng = 4.0
    num = total/num_classes
    for i in xrange(num_classes):
        gmm.set_nth_mean(np.array([Math.random(-rng, rng) for j in xrange(2)]), i)
        cov_tmp = Math.normal_random(0.2, 0.1)
        cov = np.array([[1.0, cov_tmp], [cov_tmp, 1.0]], dtype=float)
        gmm.set_nth_cov(cov, i)

    data=[]
    labels=[]
    for i in xrange(num_classes):
        coef = np.zeros(num_classes)
        coef[i] = 1.0
        gmm.set_coef(coef)
        data.append(np.array([gmm.sample() for j in xrange(num)]).T)
        labels.append(np.array([i for j in xrange(num)]))

    data = np.hstack(data)
    data = data / (2.0 * rng)
    xmin = np.min(data[0,:])
    ymin = np.min(data[1,:])
    labels = np.hstack(labels)
    toy_data = []
    for i in xrange(num_classes*num):
        toy_data.append( {  'x': data[0, i] - xmin,
                            'y': data[1, i] - ymin,
                            'label': float(labels[i])})
    return HttpResponse(json.dumps(toy_data))

def generate(request):
    if (request.POST['action'] and request.POST['action'] == 'classify'):
        if (request.POST['generator_type']=='checkboard'):
            return generate_checkboard_data(request)
        else:
            return generate_gmm_classification_data(request)
    else:
        return generate_regression_data(request)

