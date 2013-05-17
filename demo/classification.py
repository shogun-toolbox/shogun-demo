from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json


def binary(request):
    return render_to_response("classification/binary.html", context_instance=RequestContext(request))


def multiclass(request):
    return render_to_response("classification/multiclass.html", context_instance=RequestContext(request))


def index(request):
    return render_to_response("classification/index.html", context_instance=RequestContext(request))


def perceptron(request):
    return render_to_response("classification/perceptron.html", context_instance=RequestContext(request))


def run_binary(request):
    points = json.loads(request.GET["points"])
    C = json.loads(request.GET["C"])

    try:
        features, labels = _get_binary_features(points)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        kernel = _get_kernel(request, features)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        x, y, z = classify_svm(sg.LibSVM, features, labels, kernel, C=C)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    data = {"status": "ok", "domain": [np.min(z), np.max(z)], "max": np.max(z), "min": np.min(z), "z": z.tolist()}

    return HttpResponse(json.dumps(data))


def run_multiclass(request):
    points = json.loads(request.GET["points"])
    C = json.loads(request.GET["C"])

    try:
        features, labels = _get_multi_features(points)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    try:
        kernel = _get_kernel(request, features)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        x, y, z = classify_svm(sg.GMNPSVM, features, labels, kernel, C=C)

    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    # Conrec hack: add tiny noise
    z = z + np.random.rand(*z.shape) * 0.01

    data = {"status": "ok", "domain": [0, 4], "max": np.max(z), "min": np.min(z), "z": z.tolist()}

    return HttpResponse(json.dumps(data))


def run_perceptron(request):
    points = json.loads(request.GET["points"])
    learn = json.loads(request.GET["C"])
    bias = json.loads(request.GET["sigma"])


    try:
        features, labels = _get_binary_features(points)
    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))

    try:
        z_value, z_label = classify_perceptron(sg.Perceptron, features, labels, learn, bias)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    mininum = np.min(z_value)
    maximum = np.max(z_value)

    data = {"status": "ok", "domain": [mininum, maximum], "max": maximum, "min": mininum, "z": z_value.tolist(), "z2": z_label.tolist()}

    return HttpResponse(json.dumps(data))


def _get_kernel(request, features):
    name = json.loads(request.GET["kernel"])

    if name == "gaussian":
        sigma = json.loads(request.GET["sigma"])
        kernel = sg.GaussianKernel(features, features, sigma)
    elif name == "linear":
        kernel = sg.LinearKernel(features, features)
        kernel.set_normalizer(sg.IdentityKernelNormalizer())
    elif name == "poly":
        degree = json.loads(request.GET["degree"])
        kernel = sg.PolyKernel(features, features, degree, True)
        kernel.set_normalizer(sg.VarianceKernelNormalizer())
    else:
        raise ValueError("Unknown kernel")

    return kernel


def classify_svm(classifier, features, labels, kernel, C=1):
    svm = classifier(C, kernel, labels)
    svm.train(features)

    size = 100
    x1 = np.linspace(0, 1, size)
    y1 = np.linspace(0, 1, size)
    x, y = np.meshgrid(x1, y1)

    test = sg.RealFeatures(np.array((np.ravel(x), np.ravel(y))))
    kernel.init(features, test)

    out = svm.apply(test).get_values()
    if not len(out):
        out = svm.apply(test).get_labels()
    z = out.reshape((size, size))
    z = np.transpose(z)

    return x, y, z


def classify_perceptron(classifier, features, labels, learn=1, bias=0):
    perceptron = classifier(features, labels)
    perceptron.set_learn_rate(learn)
    perceptron.set_max_iter(1000)
    perceptron.set_bias(bias)
    perceptron.train()

    size = 100
    x1 = np.linspace(0, 1, size)
    y1 = np.linspace(0, 1, size)
    x, y = np.meshgrid(x1, y1)

    test = sg.RealFeatures(np.array((np.ravel(x), np.ravel(y))))

    outl = perceptron.apply(test).get_labels()
    outv = perceptron.apply(test).get_values()

    # Normalize output
    outv /= np.max(outv)

    z_value = outv.reshape((size, size))
    z_value = np.transpose(z_value)

    z_label = outl.reshape((size, size))
    z_label = np.transpose(z_label)
    z_label = z_label + np.random.rand(*z_label.shape) * 0.01

    return z_value, z_label


def _get_binary_features(data):
    A = np.transpose(np.array(data.get("a", []), dtype=float))
    B = np.transpose(np.array(data.get("b", []), dtype=float))

    if not len(A):
        if not len(B):
            raise ValueError("0-labels")
        else:
            raise ValueError("1-class-labels")
    else:
        if not len(B):
            raise ValueError("1-class-labels")
        else:
            features = np.concatenate((A, B), axis=1)
            labels = np.concatenate((np.ones(A.shape[1]), -np.ones(B.shape[1])), axis=1)

    features = sg.RealFeatures(features)
    labels = sg.BinaryLabels(labels)

    return features, labels


def _get_multi_features(data):
    v = {"a": None, "b": None, "c": None, "d": None}
    empty = np.zeros((2, 0))
    for key in v:
        if key in data:
            v[key] = np.transpose(np.array(data[key], dtype=float))
        else:
            v[key] = empty

    n = len(set(["a", "b", "c", "d"]) & set(data.keys()))

    if not n:
        raise ValueError("0-labels")
    elif n == 1:
        raise ValueError("1-class-labels")
    else:
        features = np.concatenate(tuple(v.values()), axis=1)
        labels = np.concatenate((np.zeros(v["a"].shape[1]), np.ones(v["b"].shape[1]), 2 * np.ones(v["c"].shape[1]), 3 * np.ones(v["d"].shape[1])), axis=1)

    features = sg.RealFeatures(features)
    labels = sg.MulticlassLabels(labels)

    return features, labels

