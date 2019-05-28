import numpy as np
import shogun as sg
import json
def get_binary_features(request):
    try:
        point_set_raw = json.loads(request.POST['point_set'])
    except:
        raise ValueError("cannot read click pts")
    class_a_point_set = []
    class_b_point_set = []
    for point in point_set_raw:
        if point['label'] == 1:
            class_a_point_set.append([point['x'], point['y']])
        else:
            class_b_point_set.append([point['x'], point['y']])
    class_a = np.transpose(np.array(class_a_point_set, dtype=float))
    class_b = np.transpose(np.array(class_b_point_set, dtype=float))

    if not ( len(class_a) + len(class_b)):
        raise ValueError("labels not enough")
    else:
        features = np.concatenate((class_a, class_b), axis = 1)
        labels = np.concatenate((np.ones(class_a.shape[1]), -np.ones(class_b.shape[1])), axis = 1)

    features = sg.RealFeatures(features)
    labels = sg.BinaryLabels(labels)

    return features, labels

def get_multi_features(request):
    try:
        point_set_raw = json.loads(request.POST['point_set'])
    except:
        raise ValueError("cannot read click pts")

    x=[]
    y=[]
    labels=[]
    for pt in point_set_raw:
        x.append(float(pt['x']))
        y.append(float(pt['y']))
        labels.append(float(pt['label']))

    n = len(set(labels))

    if not n:
        raise ValueError("0-labels")
    elif n == 1:
        raise ValueError("1-class-labels")
    else:
        features = np.array([x, y])

    features = sg.RealFeatures(features)
    labels = sg.MulticlassLabels(np.array(labels))

    return features, labels
