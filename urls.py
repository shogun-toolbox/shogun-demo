from django.conf.urls import patterns, include, url

urlpatterns = patterns('demos',
    url(r'^clustering/kmeans/', 'clustering.kmeans.handler'),
    
    url(r'^regression/svr/', 'regression.svr.handler'),
    url(r'^regression/gp/', 'regression.gp.handler'),
    url(r'^regression/regression/', 'regression.regression.handler'),
    
    url(r'^classifier/binary/', 'classifier.binary.handler'),
    url(r'^classifier/perceptron/', 'classifier.perceptron.handler'),
    url(r'^classifier/multiclass/', 'classifier.multiclass.handler'),
    url(r'^classifier/gp/', 'classifier.gp.handler'),
    
    url(r'^dimred/tapkee/$', 'dimred.tapkee.entrance'),
    url(r'^dimred/tapkee/words.json', 'dimred.tapkee.words'),
    url(r'^dimred/tapkee/promoters.json', 'dimred.tapkee.promoters'),

    url(r'^application/ocr/', 'application.ocr.handler'),
    url(r'^application/language_detect/', 'application.language_detect.handler'),
    url(r'^application/arts/', 'application.arts.handler'),
    url(r'^application/asp/', 'application.asp.handler'),
    
    url(r'^misc/kernel_matrix/', 'misc.kernel_matrix.handler'),
    url(r'^misc/tree/', 'misc.tree.entrance'),
)

urlpatterns += patterns('util',
    url(r'^toy_data/generator/generate', 'generator.generate'),
    url(r'^toy_data/importer/dump', 'importer.dump'),
    url(r'^toy_data/importer/regress_dump', 'importer.regress_dump'),   
    url(r'^toy_data/importer/files', 'importer.files'),
    url(r'^data/(\w+)/(.+)', 'data.serve'),
)                                                            
