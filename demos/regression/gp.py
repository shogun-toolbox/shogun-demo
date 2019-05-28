from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from common.kernel import get_kernel
from util import read_demo_description

import shogun as sg
import numpy as np
import numpy.random as rnd
import json
import os

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    elif request.path==os.sep.join(["","regression", "gp", "TrainGP"]):
        return gaussian_process(request)
    else:
        return plot_predictive(request)

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'kernel',
            'argument_items': ['GaussianKernel', 'PolynomialKernel', 'LinearKernel'],
            'argument_default': 'GaussianKernel',
            'argument_explain': 'Your choice for the covariance function'
        },
        {
            'argument_type': 'select',
            'argument_label': 'Inference Method',
            'argument_name': 'inf',
            'argument_items': ['ExactInferenceMethod', 'FITCInferenceMethod'],
            'argument_default': 'ExactInferenceMethod',
            'argument_explain': 'Your choice for the Inference method'
        },
        {
            'argument_type': 'integer',
            'argument_name': 'degree',
            'argument_default': '5',
            'argument_explain': 'The degree to use with the PolynomialKernel'
        },
        {
            'argument_type': 'decimal',
            'argument_label': 'Kernel Width',
            'argument_name': 'sigma',
            'argument_default': '1.0',
            'argument_explain': 'The sigma to use in the GaussianKernel'
        },
        {
            'argument_type': 'decimal',
            'argument_label': 'Noise Level',
            'argument_name': 'noise_level',
            'argument_default': '0.1',
            'argument_explain': 'The noise level of the training points'
        },
        {
            'argument_type': 'decimal',
            'argument_name': 'scale',
            'argument_label': 'Kernel scaling',
            'argument_default' : '1.0',
            'argument_explain': 'The scale for kernel'},

        {
            'argument_type': 'select',
            'argument_label': 'Learn parameters',
            'argument_name': 'learn',
            'argument_items':['No',
                              'ML2'],
            'argument_explain':'Learn parameters using model selection'},

        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'TrainGP',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'plot_predictive',
                                'button_type': 'json_up_down_load'},
                               {'button_name': 'clear'}]
        }
    ]
    toy_data_arguments = [
        {
            'problem_type': 'regression',
            }
        ]

    properties = { 'title': 'Gaussian Process Regression',
                   'template': {'type': 'coordinate-2dims',
                                'mouse_click_enabled': 'both',
                                'coordinate_system': {'horizontal_axis': {'range': [-5, 5]},
                                                      'vertical_axis': {'range': [-5, 5]}},
                                'heatmap': { 'contour': True },
                                'description': read_demo_description.read_description(__file__)},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Arguments',
                           'panel_property': arguments
                       },
                       {
                           'panel_name': 'toy_data',
                           'panel_label': 'Toy Data',
                           'panel_property': toy_data_arguments
                       }]}
    return render_to_response("regression/gaussian_process.html",
                              properties, context_instance = RequestContext(request))

def gaussian_process(request):
    result = []
    try:
        arguments, model_sel_error = _read_toy_data(request)
        if model_sel_error:
            return HttpResponse(json.dumps({"status": ("Model Selection " 
            "allowed only for less than 100 samples due to computational costs")}))
        result = _process(*arguments)
    except:
        raise ValueError("Argument Error")

    return HttpResponse(json.dumps(result))

def plot_predictive(request):
    result=[]
    try:
        arguments, model_sel_error = _read_toy_data(request)
        if model_sel_error:
            return HttpResponse(json.dumps({"status": ("Model Selection " 
            "allowed only for less than 100 samples due to computational costs")}))
        result = _predictive_process(*arguments)
    except:
        raise ValueError("Argument Error")
    
    return HttpResponse(json.dumps(result))

def _read_toy_data(request):
    y_set = []
    x_set = []
    x_set_induc=[]
    points=[]
    points_induc=[]
    model_sel_error=False
    toy_data = json.loads(request.POST['point_set'])
    for pt in toy_data:
        if int(pt['label'])==1:
            points.append(pt)
        elif pt['label']==-1:
            points_induc.append(pt)

    for pt in points:
        y_set.append(float(pt["y"]))
        x_set.append(float(pt["x"]))

    for pt in points_induc:
        x_set_induc.append(float(pt["x"]))

    noise_level = float(request.POST['noise_level'])
    scale = float(request.POST['scale'])
    inf = request.POST['inf']
    domain = json.loads(request.POST['axis_domain'])
    
    labels = np.array(y_set, dtype = np.float64)
    num = len(x_set)
    if num == 0:
        raise Http404
    examples = np.zeros((1, num))
    for i in xrange(num):
        examples[0,i] = x_set[i]
    feat_train = sg.RealFeatures(examples)
    labels = sg.RegressionLabels(labels)

    #Get inducing points
    num_induc = len(x_set_induc)
    
    if num_induc != 0:
        examples_induc = np.zeros((1, num_induc))
        for i in xrange(num_induc):
            examples_induc[0,i] = x_set_induc[i]
        feat_train_induc = sg.RealFeatures(examples_induc)
    elif num_induc == 0:
        feat_train_induc = None

    kernel = get_kernel(request, feat_train)
    try:
        learn = request.POST["learn"]
    except:
        raise ValueError("Argument Error")

    if int(feat_train.get_num_vectors()) > 100 and learn == "ML2":
        model_sel_error=True

    return (feat_train, labels, noise_level, scale, kernel, domain, learn, feat_train_induc, inf), model_sel_error

def _process(feat_train, labels, noise_level, scale, kernel, domain, learn, feat_induc, inf_select, return_values=False):
    n_dimensions = 1

    likelihood = sg.GaussianLikelihood()
    if learn == 'ML2':
        likelihood.set_sigma(1)
    else:
        likelihood.set_sigma(noise_level)
    covar_parms = np.log([2])
    hyperparams = {'covar': covar_parms, 'lik': np.log([1])}

    # construct covariance function
    SECF = kernel
    covar = SECF
    zmean = sg.ZeroMean()
    if str(inf_select) == 'ExactInferenceMethod':
        inf = sg.ExactInferenceMethod(SECF, feat_train, zmean, labels, likelihood)
        if learn == 'ML2':
            inf.set_scale(1)
        else:
            inf.set_scale(scale)
    elif str(inf_select) == 'FITCInferenceMethod':
        if feat_induc != None:
            inf = sg.FITCInferenceMethod(SECF, feat_train, zmean, labels, likelihood, feat_induc)
            if learn == 'ML2':
                inf.set_scale(1)
            else:
                inf.set_scale(scale)
        elif feat_induc == None:
            raise ValueError("Argument Error")

        

    # location of unispaced predictions
    size=75
    x_test = np.array([np.linspace(domain['horizontal'][0],
                                   domain['horizontal'][1], 
                                   size)])
    feat_test = sg.RealFeatures(x_test)

    gp = sg.GaussianProcessRegression(inf)

    best_width=0.0
    best_scale=0.0
    best_sigma=0.0

    if learn == 'ML2':
        grad = sg.GradientEvaluation(gp, feat_train, labels, sg.GradientCriterion(), False)
        grad.set_function(inf)
        grad_search = sg.GradientModelSelection(grad)
        best_combination = grad_search.select_model()
        best_combination.apply_to_machine(gp)
        best_scale = inf.get_scale()
        best_sigma= sg.GaussianLikelihood.obtain_from_generic(inf.get_model()).get_sigma()
        if kernel.get_name() == 'GaussianKernel':
            best_width = sg.GaussianKernel.obtain_from_generic(inf.get_kernel()).get_width()
        
    gp.train()
    
#    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_COV)
    covariance = gp.get_variance_vector(feat_test)
#    gp.set_return_type(sg.GaussianProcessRegression.GP_RETURN_MEANS)
    predictions = gp.get_mean_vector(feat_test)

    result = []
    for i in xrange(len(feat_test.get_feature_matrix()[0])):
        result.append({'x': feat_test.get_feature_matrix()[0][i],
                       'y': predictions[i],
                       'range_upper': predictions[i]+2*np.sqrt(covariance[i]),
                       'range_lower': predictions[i]-2*np.sqrt(covariance[i]),
                       'best_width': float(best_width),
                       'best_scale': float(best_scale),
                       'best_sigma': float(best_sigma)
                       })
        
    if not return_values:
        return result
    elif return_values:
        return covariance, predictions, best_width, best_scale, best_sigma

def _predictive_process(feat_train, labels, noise_level, scale, kernel, domain, learn, feat_induc, inf_select):
    variances, means, best_width, best_scale, best_sigma = _process(feat_train, labels, noise_level, scale, kernel, domain, learn, feat_induc, inf_select, True)
    size=75
    x_test = np.array([np.linspace(domain['horizontal'][0], domain['horizontal'][1], size)])
    feat_test = sg.RealFeatures(x_test)    
    y1 = np.linspace(domain['vertical'][0], domain['vertical'][1], 50)
    D=np.zeros((len(y1), size))

    # evaluate normal distribution at every prediction point (column)
    for j in range(np.shape(D)[1]):
        # create gaussian distributio instance, expects mean vector and covariance matrix, reshape
        gauss = sg.GaussianDistribution(np.array(means[j]).reshape(1,), np.array(variances[j]).reshape(1,1))
    
        # evaluate predictive distribution for test point, method expects matrix
        D[:,j] = np.exp(gauss.log_pdf_multiple(y1.reshape(1,len(y1))))
    
    z=np.transpose(D)
    z_max = np.nanmax(z)
    z_min = np.nanmin(z)
    z_delta = 0.1*(np.nanmax(z)-np.nanmin(z))

    result = []
    for i in xrange(len(feat_test.get_feature_matrix()[0])):
        result.append({'x': feat_test.get_feature_matrix()[0][i],
                       'y': means[i],
                       'range_upper': means[i]+2*np.sqrt(variances[i]),
                       'range_lower': means[i]-2*np.sqrt(variances[i]),
                       'best_width': float(best_width),
                       'best_scale': float(best_scale),
                       'best_sigma': float(best_sigma),
                       "status": "ok",
                       "domain": [z_min-z_delta, z_max+z_delta],
                       "max": z_max+z_delta,
                       "min": z_min-z_delta,
                       "z": z.tolist()
                       })


    return result
