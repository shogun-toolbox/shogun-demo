from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import demo
import modshogun as sg
import numpy as np
import json

def entrance(request):
    arguments = [
        {
            'argument_type': 'select',
            'argument_name': 'demo_switch',
            'argument_label': 'Feature Type',
            'argument_items': ['MIT_CBCL_faces_embedding',
                               'words_embedding',
                               'MNIST_digits_embedding',
                               'promoters_embedding',
                               'faces_embedding'],
            },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'show'},
                               {'button_name': 'clear'}],
            }
        ]
    properties = {'title': 'Dimension Reduction',
                  'template': {'type': 'coordinate-2dims',
                               'mouse_click_enabled': 'none'},
                  'panels':[
                      {
                          'panel_name': 'arguments',
                          'panel_label': 'Arguments',
                          'panel_property': arguments
                      }]}
                
    return render_to_response("tapkee/index.html",
                              properties,
                              context_instance = RequestContext(request))
