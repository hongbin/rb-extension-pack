from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template.context import RequestContext

import RBBugTracker
from RBBugTracker import extension


def configure(request,
            template_name='index.html',
            failed=None):
    tracker_links = {}
    for name, tracker_info in extension.BUG_TRACKER_INFO.items():
        tracker_links[name] = 'http://%s/RBBugTracker/%s' \
                % (Site.objects.get_current().domain,
                   tracker_info['url'])
    
    return render_to_response(template_name, RequestContext(request, {
        'links': tracker_links
    }))
