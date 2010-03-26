from django.conf.urls.defaults import *

urlpatterns = patterns('testhelper.testingapp.views',
    url(r'^multi-template/$', 'multi_template', name="multi_template"),
)