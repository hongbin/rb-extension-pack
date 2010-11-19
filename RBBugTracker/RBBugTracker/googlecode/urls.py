from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('RBBugTracker.googlecode.views',
    (r'^$', 'configure'),
    (r'^save_username/$', 'save_username'),
    (r'^what_next/$', 'what_next'),
)
