from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('RBBugTracker.views',
    (r'^$', 'configure'),
    (r'^storetoken/$', 'store_token')
)
