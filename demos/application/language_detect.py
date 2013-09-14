from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from demos import application
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
                                'caption': 'Enter a sentence to classify'},
                   'panels': [
                       {
                           'panel_name': 'arguments',
                           'panel_label': 'Dashboard',
                           'panel_property': arguments,
                       },
                       {
                           'panel_name': 'about',
                           'panel_label': 'About',
                           'panel_property': 'van51',
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
