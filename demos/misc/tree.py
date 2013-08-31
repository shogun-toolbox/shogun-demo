from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import modshogun as sg
import numpy as np
import json

def entrance(request):
    properties = {
        'title': 'tree',
        'template': {'type': 'tree'}
    }
    return render_to_response("tree/index.html",
                              properties,
                              context_instance = RequestContext(request))
