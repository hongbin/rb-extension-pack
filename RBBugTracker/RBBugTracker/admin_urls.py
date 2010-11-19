from django.conf.urls.defaults import patterns


urlpatterns = patterns('RBBugTracker.views',
    (r'^$', 'configure'),
)
