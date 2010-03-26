from django.conf.urls.defaults import *

urlpatterns = patterns('testhelper.testingapp.views',
    url(r'^multi-template/$', 'multi_template', name="multi_template"),
    url(r'^single-template/$', 'single_template', name="single_template"),
    url(r'^json/valid/$', 'json', {'template': 'valid.json'}, name="single_template"),
    url(r'^json/invalid/$', 'json', {'template': 'invalid.json'}, name="single_template"),
    
)