# BugTracker extension for Review Board.
from django.conf import settings

from djblets.extensions.base import Settings
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import DashboardHook

from RBBugTracker.googlecode import GoogleCode


_extension = None

class RBBugTrackerDashboardHook(DashboardHook):
    def get_entries(self):
        return [{
            'label': 'RBBugTracker',
            'url': settings.SITE_ROOT + 'RBBugTracker/',
        }]

class RBBugTracker(Extension):
    is_configurable = True
    bug_tracker = None

    def __init__(self):
        Extension.__init__(self)                
        self.dashboard_hook = RBBugTrackerDashboardHook(self)       
        global _extension
        _extension = self
        self.bug_tracker = GoogleCode(self) 

def get_instance():
    return _extension
