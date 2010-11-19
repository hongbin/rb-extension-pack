from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.core.urlresolvers import get_resolver
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from djblets.extensions.base import Settings

from reviewboard.reviews.models import ReviewRequest, Review
from reviewboard.reviews.signals import review_request_published, \
                                        review_published, reply_published

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


google_settings = None

class GoogleCode(object):
    """
    A wrapper class for GoogleCode issue tracker.
    """    
    def __init__(self, extension):
        # try to load settings from database if any.
        self.extension = extension
        global google_settings
        google_settings = Settings(extension)
        google_settings.load()

        # instantiate hosting client
        self.client = ProjectHostingClient()

        # if an token was stored in database, use it
        token = google_settings.get('token')
        if token:
            self.client.auth_token = AuthSubToken(token)

    def notify_bug_tracker(self, review_request, comment, sig_type):
        """
        This function will first get a bugs list form request's repository
        and try to post comments on every issues in the list.
        """
        bugs = review_request.get_bug_list()
        review_url = review_request.get_absolute_url()
        repository = review_request.repository
        project_name = repository.name
        user = get_username()
        comment += "More information: "
        comment += 'http://%s%s' % (Site.objects.get_current().domain,
                                        review_url)

        # notify every issues associated if the signal type was selected
        for bug in bugs:
            if ((sig_type == 'REVIEW_PUBLISHED' and get_review_checked())\
                or (sig_type == 'REVIEW_REQUEST_PUBLISHED' \
                    and get_review_request_checked())\
                or (sig_type == 'REPLY_PUBLISHED' and get_reply_checked())
            ):
                #DEBUG
                #print bug
                #print project_name
                #print comment
                #print user                

                self.client.update_issue(project_name, bug, user,
                    comment=comment)

def get_review_checked():    
    return google_settings.get('review_checked')

def get_review_request_checked():
    return google_settings.get('review_request_checked')

def get_reply_checked():
    return google_settings.get('reply_checked')

def get_username():
    return google_settings.get('username')

def get_token():
    return google_settings.get('token')
