from django.http import HttpResponse, Http404
from django.conf import settings
import h5py, json

TOY_DATA_DIR = 'data/'
TOY_DATA_SET = {
    'australian': 'toy/australian.libsvm.h5',
}

def files(request):
    return {'data_sets': TOY_DATA_SET.keys}

def dump(request):
    try:
        data_set = request.POST['data_set']
        feature1 = int(request.POST['feature1'])
        feature2 = int(request.POST['feature2'])
        f = h5py.File(TOY_DATA_DIR +
                      TOY_DATA_SET[data_set], 'r')
        features = f["/data/data"]
        label = f["/data/label"]
    except:
        raise Http404
    
    toy_data = []
    for i in xrange(len(features[0])):
        toy_data.append( {'x': features[feature1][i],
                          'y': features[feature2][i],
                          'label': label[i][0]})
    return HttpResponse(json.dumps(toy_data))
