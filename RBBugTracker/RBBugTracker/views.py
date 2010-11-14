import os
from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from djblets.extensions.base import Settings
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import DashboardHook, URLHook

import RBBugTracker

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core
import gdata.service


def configure(request,
            template_name='RBBugTracker/configure.html'):
    """
    In order to use this extension, user need to get an security token
    from GoogleCode. This function provide a link for user to get the
    token. That token will be used by this extension to post comments
    on issues on behalf of client.
    """
    next = 'http://%s%s' % (Site.objects.get_current().domain,
                            reverse("RBBugTracker.views.store_token"))
    link = gdata.service.GDataService().GenerateAuthSubURL(next,
                        ('http://code.google.com/feeds/issues',),
                        secure=False, session=True)
    
    return render_to_response(template_name, RequestContext(request, {
        'link': link
    }))

def store_token(request,
                template_name='RBBugTracker/configure.html'):
    """
    If the users have been successfully authenticated to GoogleCode,
    GoogleCode should make a request to this page with an token.
    We store upgrade and store that token.
    """
    client = gdata.projecthosting.client.ProjectHostingClient()
    token, scopes = gdata.gauth.auth_sub_string_from_url(
        request.build_absolute_uri())
    
    if (token):
        # Store the token and the scopes of that token into database
        extension = RBBugTracker.extension.get_instance()        
        settings = Settings(extension)
        settings['token'] = token
        settings.save()

        # update the GoogleCode instance to use the new token
        extension.bug_tracker.update_token()

        return render_to_response(template_name, RequestContext(request, {
            'success': 'success'
        }))    

    return render_to_response(template_name, RequestContext(request))
