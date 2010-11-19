# BugTracker extension for Review Board.
from django.conf import settings
from django.conf.urls.defaults import patterns, include

from djblets.extensions.base import Settings

from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import URLHook
from reviewboard.reviews.models import ReviewRequest, Review
from reviewboard.reviews.signals import review_request_published, \
                                        review_published, reply_published

import RBBugTracker

"""
directory:  The sub-folder which contain the specific bug tracker code,
            including the 'module' below. This folder should be under currect
            directory.
module:     The module which contain the 'class' below.
class:      The bug tracker wrapper class. This class should have a function
            'notify_bug_tracker'. This function will be called to notify issue
            tracker about the status of code review.
url:        The mapping url to the specific bug tracker.
            'http://domain/RBBugTracker/%s' % url should form the absolute
            address to the specific bug tracker.
host:       The hosting address of specific bug tracker.
"""
BUG_TRACKER_INFO = \
{'googlecode':
     {'directory': 'googlecode', 
      'module': 'googlecode',
      'class': 'GoogleCode',
      'url': 'googlecode/',
      'host': 'http://code.google.com/',},
}

extension = None

class RBBugTracker(Extension):
    """
    This extension is for automatically posting comments on issue(s) when the
    status of its associated code review changed.

    The goal of design is to avoid hard coding to specific type of bug trackers.
    In other words, adding support for an new bug tracker should be easy and
    the changed on bug tracker should not affect other tracker. The solution is
    to put the bug tracker specific information in the list BUG_TRACKER_INFO.
    As a result, that list is the centralized place to looking for bug trackers
    specific information. Every newly added bug tracker should modify that
    list only.
    """
    is_configurable = True
    bug_trackers = {}

    def __init__(self):
        """
        Instantiate and setup all supported bug trackers. This function will play
        with the list BUG_TRACKER_INFO to setup the urls, import the modules and
        call the constructor for every bug trackers. Finally, it will setup the
        event handlers for RB signals.
        """
        Extension.__init__(self)    
        global extension
        extension = self

        global BUG_TRACKER_INFO
        for name, info in BUG_TRACKER_INFO.items():
            try:
                # setup urls mapping for bug tracker
                # Eg: googlecode => http://domain/RBBugTracker/googlecode/
                self.url_hook = URLHook(self, patterns('',
                        ('^RBBugTracker/%s' % info['url'],
                            include('RBBugTracker.%s.urls' % info['directory']))))

                # try to import bug tracker module into current scope
                # Eg: from RBBugTracker.googlecode.googlecode import GoogleCode
                import_stmt = 'RBBugTracker.%s.%s' \
                            % (info['directory'], info['module'])            
                module = __import__(import_stmt, globals(), locals(),
                                    [info['class']])
                
                # construct the bug tracker object and cash it in a dict
                # Eg: self.bug_trackers['googlecode'] = GoogleCode(extension)
                self.bug_trackers[name] = eval('module.%s(extension)' \
                                               % info['class'])
            except ImportError:
                print 'ImportError raised: cannot import module "%s"' \
                      % import_stmt
            except:
                print 'Exception occurred when installing bug tracker %s'\
                      % name

        # setup the event handlers
        review_request_published.connect(self._review_request_published,
                                    sender=ReviewRequest,
                                    dispatch_uid="RBBugTracker")
        review_published.connect(self._review_published,
                                sender=Review,
                                dispatch_uid="RBBugTracker")
        reply_published.connect(self._reply_published,
                                sender=Review,
                                dispatch_uid="RBBugTracker")
        
    def _review_request_published(self, user,
                                  review_request, changedesc, **kwargs):
        """
        Handle review_request_published signal
        """
        print "_review_request_published: %s" % user
        self.comment = user.username + \
                       " has created an code review request for this issue.\n"
        self._notify_bug_tracker(review_request,
                                 self.comment, 'REVIEW_REQUEST_PUBLISHED')
                
    def _review_published(self, sender, user, review, **kwargs):
        """
        Handle review_published signal
        """
        print "_review_published: %s" % user
        self.comment = user.username + \
                       " has published an code review for this issue.\n"
        self._notify_bug_tracker(review.review_request,
                                 self.comment, 'REVIEW_PUBLISHED')

    def _reply_published(self, sender, user, reply, **kwargs):
        """
        Handle reply_published signal
        """
        print "_reply_published: %s" % user
        self.comment = user.username + \
                       " has replied the code review for this issue.\n"
        self._notify_bug_tracker(reply.review_request,
                                 self.comment, 'REPLY_PUBLISHED')

    def _notify_bug_tracker(self, review_request, comment, sig_type):
        """
        From a list of well-known bug trackers, find the one which match the
        request's repository and invoke the notify_bug_tracker method
        """
        if self.registration.enabled:
            for name, obj in self.bug_trackers.items():            
                if review_request.repository.bug_tracker.find(
                                    BUG_TRACKER_INFO[name]['host']) != -1:
                    # notify issue tracker
                    # handle exception globally to make sure RB will never crash
                    #try:
                        obj.notify_bug_tracker(review_request,
                                                 comment, sig_type)
                    #except:
                        #print 'Exception occurred when calling ' \
                          #    + '_notify_bug_tracker()'
