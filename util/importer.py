from django.http import HttpResponse, Http404
import settings
import h5py, json
import shogun as sg

TOY_DATA_DIR = settings.DATA_PATH+'/toy/'
REGRESS_DATA_DIR = settings.DATA_PATH+'/multiclass/categorical_dataset/'
TOY_DATA_SET = {
    'australian': 'australian.libsvm.h5',
    'diabetes': 'diabetes_scale.svm'
}
REGRESS_DATA_SET = {
        'boston_housing': 'fm_housing.dat'
        }
REGRESS_LABELS={
        'boston_housing': 'housing_label.dat'        
        }

def classify_dump(request):
    try:
        data_set = request.POST['data_set']    
        h_feature = request.POST['h_feature']
        f=sg.SparseRealFeatures()
        #Load the file and generate labels.
        trainlab=f.load_with_labels(sg.LibSVMFile(TOY_DATA_DIR + TOY_DATA_SET[data_set],))
        #Get the feature matrix
        mat=f.get_full_feature_matrix()
        if h_feature == 'GLUC':
            h_feat = mat[1]
        elif h_feature == 'BP':
            h_feat = mat[2]
        elif h_feature == 'SKIN':
            h_feat = mat[3]
        elif h_feature == 'INSUL':
            h_feat = mat[4]
        elif h_feature == 'BMI':
            h_feat = mat[5]
        elif h_feature == 'AGE':
            h_feat = mat[6]

        v_feature = request.POST['v_feature']
        if v_feature == 'GLUC':
            v_feat = mat[1]
        elif v_feature == 'BP':
            v_feat = mat[2]
        elif v_feature == 'SKIN':
            v_feat = mat[3]
        elif v_feature == 'INSUL':
            v_feat = mat[4]
        elif v_feature == 'BMI':
            v_feat = mat[5]
        elif v_feature == 'AGE':
            v_feat = mat[6]
    except:
        raise Http404
    
    toy_data = []
    for i in xrange(len(mat[0])):
        toy_data.append( {'x': h_feat[i],
                          'y': v_feat[i],
                          'label': trainlab[i]})
    return HttpResponse(json.dumps(toy_data))

def regress_dump(request):
    try:
        data_set = request.POST['data_set']
        feature = request.POST['feature']


        temp_feats=sg.RealFeatures(sg.CSVFile(REGRESS_DATA_DIR + REGRESS_DATA_SET[data_set]))
        labels=sg.RegressionLabels(sg.CSVFile(REGRESS_DATA_DIR + REGRESS_LABELS[data_set]))
        lab=labels.get_labels()

        #rescale to 0...1
        preproc=sg.RescaleFeatures()
        preproc.init(temp_feats)
        temp_feats.add_preprocessor(preproc)
        temp_feats.apply_preprocessor(True)
        mat = temp_feats.get_feature_matrix()

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
                          'y': lab[i],
                          'label': float(0)})
    return HttpResponse(json.dumps(toy_data))

