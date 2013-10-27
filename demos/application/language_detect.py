from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from demos import application
from util import read_demo_description
import json

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return recognize(request)

def entrance(request):
    arguments = [
        {
            'argument_type': 'div',
            'argument_name': 'Language:',
            'argument_id': 'result',
        },
        {
            'argument_type': 'button-group',
            'argument_items': [{'button_name': 'recognize'},
                               {'button_name': 'clear' }]
        }]
    properties = { 'title' : 'Language Detection',
                   'template': {'type': 'text',
                                'caption': 'Enter a sentence to classify:',
                                'description': read_demo_description.read_description(__file__)},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Dashboard',
                           'panel_property': arguments,
                       },
                       {
                           'panel_name': 'about',
                           'panel_label': 'About',
                           'panel_property': 'Developed by <a target="_blank" href="https://github.com/van51">van51</a>',
                        }
                    ]
                 }
    return render_to_response("application/language_detect.html",
                              properties,
                              context_instance = RequestContext(request))

def recognize(request):
    try:
        sample_text=request.POST.get('text').encode('utf-8')
        if sample_text.strip() == '':
            raise Http404
        lang = application.lc.classify_doc(sample_text)
        return HttpResponse(json.dumps({'predict': lang}))
    except:
        raise Http404
