from django.conf import settings

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
from gdata.auth import AuthSubToken
from gdata.projecthosting.client import ProjectHostingClient


class GoogleCode(object):
    """
    A wrapper class for GoogleCode issue tracker.
    """
    client = gdata.projecthosting.client.ProjectHostingClient()
    
    def __init__(self, extension):
        self.extension = extension
        self.settings = Settings(extension)
        self.settings.load()
        self.update_token()            

        review_request_published.connect(self._review_request_published,
                                  sender=ReviewRequest)
        review_published.connect(self._review_published,
                                  sender=Review)
        reply_published.connect(self._reply_published,
                                  sender=Review)

    def update_token(self):
        """
        If the hosting client don't have an session token, we get the
        signal-use token from settings and use it to apply an session
        token
        """
        if (self.client.auth_token and self.settings.get('token')):
            # Upgrade the single-use AuthSub token to a multi-use
            # session token.
            self.client.auth_token = self.client.upgrade_token(
                gdata.gauth.AuthSubToken(self.settings['token']))

    def _review_request_published(self, user, review_request, changedesc, **kwargs):
        print "_review_request_published: %s" % user

    def _review_published(self, sender, user, review, **kwargs):
        print "_review_published: %s" % user
        self._notify_bug_tracker('review published', sender, user, review)

    def _reply_published(self, sender, user, reply, **kwargs):
        print "_reply_published: %s" % user
        self._notify_bug_tracker('reply published',  sender, user, None, reply)

    def _notify_bug_tracker(self, message=None, sender=None, user=None, review=None, reply=None):
        #for test
        query = gdata.projecthosting.client.Query(issue_id = '193')
        feed = self.client.get_issues('reviewboard', query=query)
        for issue in feed.entry:
            print issue.title.text
            
        #TODO: avoid hard code project name and issue id.
        #client.update_issue('reviewboard', '193', user, comment='My comment here.',
        #                    summary='New Summary', status='Accepted', owner=assignee,
        #                    labels=['-label0', 'label1'], ccs=[owner])
        

