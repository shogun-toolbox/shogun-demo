from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shogun_demo.views.home', name='home'),
    url(r'^clustering/entrance', 'demo.clustering.entrance'),
    url(r'^clustering/cluster', 'demo.clustering.cluster'),
    url(r'^svr/entrance', 'demo.svr.entrance'),
    url(r'^svr/regress', 'demo.svr.point'),
    url(r'^classification/index', 'demo.classification.index'),
    url(r'^classification/binary/entrance', 'demo.classification_binary.entrance'),
    url(r'^classification/binary/classify', 'demo.classification_binary.classify'),
    url(r'^classification/perceptron/entrance', 'demo.classification_perceptron.entrance'),
    url(r'^classification/perceptron/classify', 'demo.classification_perceptron.classify'),
    url(r'^classification/binary', 'demo.classification.binary'),
    url(r'^classification/run_binary', 'demo.classification.run_binary'),
    url(r'^classification/multiclass', 'demo.classification.multiclass'),
    url(r'^classification/run_multiclass', 'demo.classification.run_multiclass'),
    url(r'^classification/perceptron', 'demo.classification.perceptron'),
    url(r'^classification/run_perceptron', 'demo.classification.run_perceptron'),
    url(r'^gp/entrance', 'demo.gp.entrance'),
    url(r'^gp/create_toy_data', 'demo.gp.create_toy_data'),
    url(r'^gp/load_toy_data', 'demo.gp.load_toy_data'),
    url(r'^gp/TrainGP', 'demo.gp.train'),
    url(r'^kernel_matrix/entrance', 'demo.kernel_matrix.entrance'),
    url(r'^kernel_matrix/generate', 'demo.kernel_matrix.generate'),
    url(r'^ocr/entrance', 'demo.ocr.entrance'),
    url(r'^ocr/recognize', 'demo.ocr.recognize'),
    url(r'^tapkee/entrance', 'demo.tapkee.entrance'),
    url(r'^toy_data/generator/generate', 'toy_data.generator.generate'),
    url(r'^toy_data/importer/dump', 'toy_data.importer.dump'),
    url(r'^data/(\w+)/(.+)', 'common.data.serve'),
                                                            
    # url(r'^shogun_demo/', include('shogun_demo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
