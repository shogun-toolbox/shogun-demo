from django.http import HttpResponse
import json
import zipfile

archives = {
    'mnist': 'data/tapkee/mnist.zip',
    'faces_transparent': 'data/tapkee/faces_transparent.zip',
    'oks': 'data/tapkee/oks.zip',
}

def serve(request, archive_name, file_name):
    try:
        z = zipfile.ZipFile(archives[archive_name], "r")
        content = z.read(file_name)
        return HttpResponse(content,mimetype="image/png")
    except:
        return json.dumps({'status': 'exception'})
