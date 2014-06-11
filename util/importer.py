from django.http import HttpResponse, Http404
import settings
import h5py, json
import modshogun as sg

TOY_DATA_DIR = settings.DATA_PATH+'/toy/'
TOY_DATA_SET = {
    'australian': 'australian.libsvm.h5',
    'boston_housing': 'housing_scale.svm',
}

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

def regress_dump(request):
    try:
        data_set = request.POST['data_set']
        feature = request.POST['feature']
        f=sg.SparseRealFeatures()
        #Load the file and generate labels.
        trainlab=f.load_with_labels(sg.LibSVMFile(TOY_DATA_DIR + TOY_DATA_SET[data_set],))
        #Get the feature matrix
        mat=f.get_full_feature_matrix()
        if feature == 'CRIM':
            feat = mat[0]
        elif feature == 'DIS':
            feat = mat[7]
        elif feature == 'INDUS':
            feat = mat[2]
        elif feature == 'LSTAT':
            feat = mat[12]
    except:
        raise Http404

    toy_data = []
    for i in xrange(len(feat)):
        toy_data.append( {'x': feat[i],
                          'y': trainlab[i],
                          'label': float(0)})
    return HttpResponse(json.dumps(toy_data))

