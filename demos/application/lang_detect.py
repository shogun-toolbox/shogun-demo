from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

def handler(request):
	if request.method == 'GET':
		return entrance(request)
	else:
		return recognize(request)

def entrance(request):
	properties = { 'title' : 'Language Detection Demo' }
                   #'template': {'type': 'drawing'},
                   #'panels': [
                   #    {
                   #        'panel_name': 'preview',
                   #        'panel_label': 'Preview'}]}
	return render_to_response("application/lang_detect.html",
								properties,
								context_instance = RequestContext(request))

def recognize(request):
	try:
		text = json.loads(request.POST['text'])
		lang = lc.classify_doc(text)
		return HttpResponse(json.dumps({'predict': lang}))
	except:
		import traceback
		print traceback.format_exc()
		raise Http404
