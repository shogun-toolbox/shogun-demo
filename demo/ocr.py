from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json

def entrance(request):
    properties = { 'title' : 'Digit Recognize',
                   'template': {'type': 'drawing'},
                   'panels': [
                       {
                           'panel_name': 'result',
                           'panel_label': 'Digit'}]}
    return render_to_response("ocr/index.html",
                              properties,
                              context_instance = RequestContext(request))

