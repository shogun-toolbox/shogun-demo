from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from demos import application
from util import read_demo_description

import modshogun as sg
import numpy as np
import json


MATIX_IMAGE_SIZE = 16
FEATURE_RANGE_MAX = 1.0
NEAR_ZERO_POS = 1e-8
NEAR_ONE_NEG = 1-NEAR_ZERO_POS

def handler(request):
    if request.method == 'GET':
        return entrance(request)
    else:
        return recognize(request)


def entrance(request):
    properties = { 'title' : 'Digit Recognize',
                   'template': {'type': 'drawing',
                                'description': read_demo_description.read_description(__file__)},
                   'panels': [
                       {
                           'panel_name': 'preview',
                           'panel_label': 'Preview'}]}
    return render_to_response("application/ocr.html",
                              properties,
                              context_instance = RequestContext(request))

def _draw_line(image, start, end):
    start = np.array(start, dtype=np.int)
    end = np.array(end, dtype=np.int)
    
    delta = abs(end - start)
    
    e = delta[0]/2.0
    x, y = start
    image[y, x] = FEATURE_RANGE_MAX
    while np.any((x, y) != end):
        if e < 0.0 or x == end[0]:
            y += -1 if start[1] > end[1] else 1
            e += delta[0]
        if e >= 0.0 and x != end[0]:
            x += -1 if start[0] > end[0] else 1
            e -= delta[1]
        image[y, x] = FEATURE_RANGE_MAX

def _get_coords(data):
    result = map(lambda line: np.array(line), data)
    result = map(lambda line: np.transpose(line), result)
    minx = 2.0
    miny = 2.0
    for line in result:
        minx = min(minx, min(line[0]))
        miny = min(miny, min(line[1]))
    for line in result:
        line[0] -= minx
        line[1] -= miny
        
    maxxy = 0.0
    for line in result: maxxy = max(maxxy, line.max())
    for line in result: line /= maxxy + NEAR_ZERO_POS

    maxx = 0.0
    maxy = 0.0
    for line in result:
        maxx = max(maxx, max(line[0]))
        maxy = max(maxy, max(line[1]))
    for line in result:
        line[0] += (1 - maxx)/2
        line[1] += (1 - maxy)/2
                                    
    result = map(lambda line: np.transpose(line), result)
    return result
        
def recognize(request):
    image = np.zeros((16, 16), dtype=np.float)
    try:
        data = json.loads(request.POST['lines'])
        coords = map(lambda line: MATIX_IMAGE_SIZE*line,
                     _get_coords(data))
        image = np.zeros((MATIX_IMAGE_SIZE, MATIX_IMAGE_SIZE),
                         dtype=np.float)
        for line in coords:
            for i in range(line.shape[0]-1):
                _draw_line(image, line[i], line[i+1])
        digit = application.ai.classify(image)
        return HttpResponse(json.dumps({'predict': digit,
                                        'thumb': image.tolist()}))
    except:
        import traceback
        print traceback.format_exc()
        raise Http404

    print image

