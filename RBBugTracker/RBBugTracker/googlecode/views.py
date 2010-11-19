from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from djblets.extensions.base import Settings

from reviewboard.reviews.models import ReviewRequest, Review
from reviewboard.reviews.signals import review_request_published, \
                                        review_published, reply_published

import googlecode
from googlecode import *

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core
import gdata.service
from gdata.gauth import AuthSubToken
from gdata.projecthosting.client import ProjectHostingClient
from gdata.service import GDataService


def configure(request,
            template_name='googlecode/configuration.html',
            failed=None,
            config_changed=None):
    """
    In order to use this extension, user need to get an security token
    from GoogleCode. This function provide a link for user to get the
    token. That token will be used by this extension to post comments
    on issues on behalf of client.
    """
    # if the configuration changed, we save it
    if (request.REQUEST.get('changed')):
        config_changed = 'yes'
        save_conf(request)
    
    next = 'http://%s/RBBugTracker/googlecode/save_username/' \
           % Site.objects.get_current().domain
    link = GDataService().GenerateAuthSubURL(next,
                        ('http://code.google.com/feeds/issues',),
                        secure=False, session=True)

    # Make sure the checkbox is checked if it was selected
    review_checked = ''
    review_request_checked = ''
    reply_checked = ''
    if get_review_checked():
        review_checked = 'checked="yes"'
    if get_review_request_checked():
        review_request_checked = 'checked="yes"'
    if get_reply_checked():
        reply_checked = 'checked="yes"'
        
    return render_to_response(template_name, RequestContext(request, {
        'login_link': link,
        'failed': failed,
        'config_changed': config_changed,
        'review_checked': review_checked,
        'review_request_checked': review_request_checked,
        'reply_checked': reply_checked,        
    }))

def save_username(request,
                  template_name='googlecode/save_username.html',
                  failed=None):
    """
    If the users have been successfully authenticated to GoogleCode,
    GoogleCode should make a request to this page with an token.
    We upgrade and store that token.

    The other case is user submit a form.
    In this case, we store the username in the form if it is not empty.
    """
    keys = request.REQUEST.keys()
    for key in keys:
        if (key == 'username'):
            # if the request contain an username key, we process it
            if (request.REQUEST['username']):
                # store the username into database
                google_settings['username'] = request.REQUEST['username']
                google_settings.save()
                # redirect to next page
                return what_next(request)
            else:
                # the case username is empty, we displayed error message
                return render_to_response(template_name,
                    RequestContext(request, {'failed': 'failed'}))

    # the case returned from GoogleCode with token attached
    client = gdata.projecthosting.client.ProjectHostingClient()
    token, scopes = gdata.gauth.auth_sub_string_from_url(
        request.build_absolute_uri())

    if (token == None):
        # handle the case authentication failed        
        return configure(request, failed='true')

    # upgrade to session token
    client.auth_token = client.upgrade_token(AuthSubToken(token, scopes))

    # Store the token and the scopes of that token into database
    if client.auth_token.token_string:
        google_settings['token'] = client.auth_token.token_string
        google_settings.save()
    else:
        failed = 'true'

    return render_to_response(template_name, RequestContext(request, {
        'failed': failed,
    }))

def what_next(request, template_name='googlecode/what_next.html'):
    googlecode_link = 'http://%s/RBBugTracker/googlecode/'\
                      % Site.objects.get_current().domain                        

    tracker_list = 'http://%s%s' % (Site.objects.get_current().domain,
                        reverse("RBBugTracker.views.configure"))

    extension_list = 'http://%s%s' % (Site.objects.get_current().domain,
                        reverse("djblets.extensions.views.extension_list"))

    return render_to_response(template_name, RequestContext(request, {
        'username': get_username(),
        'googlecode_link': googlecode_link,
        'tracker_list': tracker_list,
        'extension_list': extension_list
        }))

def save_conf(request):
    googlecode.google_settings['review_request_checked'] \
            = request.REQUEST.get('review_request')

    googlecode.google_settings['review_checked'] \
            = request.REQUEST.get('review')

    googlecode.google_settings['reply_checked'] \
            = request.REQUEST.get('reply')
    
    googlecode.google_settings.save()
