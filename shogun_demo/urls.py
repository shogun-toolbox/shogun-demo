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
    url(r'^svr/point', 'demo.svr.point'),
    url(r'^classification/index', 'demo.classification.index'),
    url(r'^classification/binary', 'demo.classification.binary'),
    url(r'^classification/run_binary', 'demo.classification.run_binary'),
    url(r'^lassification/multiclass', 'demo.classification.multiclass'),
    url(r'^classification/run_multiclass', 'demo.classification.run_multiclass'),
    url(r'^gp/entrance', 'demo.gp.entrance'),
    url(r'^gp/create_toy_data', 'demo.gp.create_toy_data'),
    url(r'^gp/train', 'demo.gp.train'),
    url(r'^kernel_matrix/entrance', 'demo.kernel_matrix.entrance'),
    url(r'^kernel_matrix/create_toy_data', 'demo.kernel_matrix.create_toy_data'),
    url(r'^kernel_matrix/generate_matrix', 'demo.kernel_matrix.generate_matrix'),
                                                            
    # url(r'^shogun_demo/', include('shogun_demo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
