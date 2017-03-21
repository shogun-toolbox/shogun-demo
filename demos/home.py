import os

from django.shortcuts import render_to_response
from util import read_demo_description

DEMOS_PATH = os.path.abspath(os.path.dirname(__file__))

DEMOS = [{"title": "A demo for support vector regression", "url": "/regression/svr/"},
              {"title": "A demo for ridge regression", "url": "/regression/regression/"},
              {"title": "A demo for gaussian process regression", "url": "/regression/gp/"},
              {"title": "A demo for binary classification", "url": "/classifier/binary/"},
              {"title": "A demo for binary perceptron", "url": "/classifier/perceptron/"},
              {"title": "A demo for multiclass classification", "url": "/classifier/multiclass/"},
              {"title": "A demo for gaussian process classification", "url": "/classifier/gp/"},
              {"title": "A demo for kernel matrix visualization", "url": "/misc/kernel_matrix/"},
              {"title": "A demo for recognizing hand-written digits.", "url": "/application/ocr/"},
              {"title": "A demo for language detection", "url": "/application/language_detect/"},
              {"title": "A demo for clustering using kmeans", "url": "/clustering/kmeans/"}]


def description_by_url(url):
    return read_demo_description.read_description(DEMOS_PATH + url[:-1] + ".py")

demo_properties = {
    'demos': map(lambda data:{"title": data['title'], "url": data['url'], "description": description_by_url(data['url'])}, DEMOS)
}
def index(request):
    return render_to_response("index.html", demo_properties)
