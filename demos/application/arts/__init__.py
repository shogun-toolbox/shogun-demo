from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from signal_sensor import SignalSensor
import json
import sys
import bz2

def_file = bz2.BZ2File('data/arts/ARTS.dat.bz2')
arts = SignalSensor()
arts.from_file(def_file)

def handler(request):
    if request.method == 'GET':
        return _entrance(request)
    else:
        return _arts(request)

arguments = [
    {
        'argument_type': 'ascii_file',
        'argument_name': 'sequence',
    },
    {
        'argument_type': 'button-group',
        'argument_items': [{'button_name': 'run'},
                           {'button_name': 'clear'}],
    }
]

properties = { 'title': 'ARTS',
               'template': {'type': 'coordinate-2dims',
                            'feature': 'binary',
                            'coordinate_range': {'horizontal': [0, 1],
                                                 'vertical': [0, 0.8]},
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'X-axis',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'Y-axis',
                                                                    'range': [0, 1]}},
                            'mouse_click_enabled': 'none'},
                'panels': [
                    {
                        'panel_name': 'arguments',
                        'panel_label': 'Dashboard',
                        'panel_property': arguments,
                    }, ]}

def _entrance(request):
    return render_to_response("application/arts.html",
                              properties,
                              context_instance=RequestContext(request))
def _arts(request):
    try:
        text = str(request.POST['seq'])
        text = text[text.index('\n') + 1:].replace('\n', '')

        preds = arts.predict(text)

        line_dot = []
        for i in range(len(preds)):
            line_dot.append({'x': i*1.0/len(preds), 'y': preds[i]})

        return HttpResponse(json.dumps(line_dot))
    except:
        import traceback
        print traceback.format_exc()
        return HttpResponse(json.dumps({"status": repr(traceback.format_exc())}))
