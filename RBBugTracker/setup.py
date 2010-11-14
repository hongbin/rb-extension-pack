from setuptools import setup, find_packages

PACKAGE="RBBugTracker"
VERSION="0.1"

setup(
    name=PACKAGE,
    version=VERSION,
    description="""BugTracker extension for Review Board""",
    author="Hongbin Lu",
    entry_points={
        'reviewboard.extensions':
        '%s = RBBugTracker.extension:RBBugTracker' % PACKAGE,
    },
    packages=['RBBugTracker'],     
    install_requires=['gdata'],
    package_data={
        'RBBugTracker': [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'templates/RBBugTracker/*.html',
            'templates/RBBugTracker/*.txt',
        ],
    }
)


