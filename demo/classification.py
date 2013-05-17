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
        x, y, z = classify(sg.LibSVM, features, labels, kernel, C=C)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    data = {"status": "ok", "domain": [-1, 1], "max": np.max(z), "min": np.min(z), "z": z.tolist()}

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
        x, y, z = classify(sg.GMNPSVM, features, labels, kernel, C=C)
    except Exception as e:
        return HttpResponse(json.dumps({"status": repr(e)}))

    # Conrec hack: add tiny noise
    z = z + np.random.rand(*z.shape) * 0.01

    data = {"status": "ok", "domain": [0, 4], "max": np.max(z), "min": np.min(z), "z": z.tolist()}

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

def classify(classifier, features, labels, kernel, C=1):
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
