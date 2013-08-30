import numpy as np
import modshogun as sg
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

    data = {'0': [], '1': [], '2': [], '3': []}

    for pt in point_set_raw:
        data[str(pt['label'])].append([float(pt['x']), float(pt['y'])])
    v = {'0': None, '1': None, '2': None, '3': None}
    print point_set_raw
    empty = np.zeros((2, 0))
    print data
    for key in v:
        if data[key]:
            v[key] = np.transpose(np.array(data[key], dtype=float))
        else:
            v[key] = empty

    n = len(set(["0", "1", "2", "3"]) & set(data.keys()))

    if not n:
        raise ValueError("0-labels")
    elif n == 1:
        raise ValueError("1-class-labels")
    else:
        features = np.concatenate(tuple(v.values()), axis=1)
        labels = np.concatenate((np.zeros(v["0"].shape[1]), np.ones(v["1"].shape[1]), 2 * np.ones(v["2"].shape[1]), 3 * np.ones(v["3"].shape[1])), axis=1)

    features = sg.RealFeatures(features)
    labels = sg.MulticlassLabels(labels)

    return features, labels
