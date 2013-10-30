from django.http import HttpResponse
import json
import zipfile
import settings

archives = {
    'mnist': settings.DATA_PATH + '/tapkee/mnist.zip',
    'faces_transparent': settings.DATA_PATH + '/tapkee/faces_transparent.zip',
    'oks': settings.DATA_PATH + '/tapkee/oks.zip',
}

def serve(request, archive_name, file_name):
    try:
        z = zipfile.ZipFile(archives[archive_name], "r")
        content = z.read(file_name)
        return HttpResponse(content,mimetype="image/png")
    except:
        return HttpResponse(json.dumps({'status': 'exception'}))
