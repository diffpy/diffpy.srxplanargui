#!/usr/bin/env python

# Installation script for dpx.pdfgetxgui

"""dpx.srxplanargui - a software for 2D powder diffraction image integration
    and error propagation

Packages:   dpx.srxplanargui
Scripts:    srxgui
"""

import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import py_compile


class custom_build_pyc(build_py):

    def byte_compile(self, files):
        for file in files:
            if file.endswith('.py'):
                py_compile.compile(file)
                os.unlink(file)

# Use this version when git data are not available, like in git zip archive.
# Update when tagging a new release.
FALLBACK_VERSION = '1.0'

# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, 'dpx', 'srxplanargui', 'version.cfg')
gitarchivecfgfile = versioncfgfile.replace('version.cfg', 'gitarchive.cfg')


def gitinfo():
    from subprocess import Popen, PIPE
    kw = dict(stdout=PIPE, cwd=MYDIR)
    proc = Popen(['git', 'describe', '--match=v[[:digit:]]*'], **kw)
    desc = proc.stdout.read()
    proc = Popen(['git', 'log', '-1', '--format=%H %at %ai'], **kw)
    glog = proc.stdout.read()
    rv = {}
    rv['version'] = '.post'.join(desc.strip().split('-')[:2]).lstrip('v')
    rv['commit'], rv['timestamp'], rv['date'] = glog.strip().split(None, 2)
    return rv


def getversioncfg():
    import re
    from ConfigParser import RawConfigParser
    vd0 = dict(version=FALLBACK_VERSION, commit='', date='', timestamp=0)
    # first fetch data from gitarchivecfgfile, ignore if it is unexpanded
    g = vd0.copy()
    cp0 = RawConfigParser(vd0)
    cp0.read(gitarchivecfgfile)
    if '$Format:' not in cp0.get('DEFAULT', 'commit'):
        g = cp0.defaults()
        mx = re.search(r'\btag: v(\d[^,]*)', g.pop('refnames'))
        if mx:
            g['version'] = mx.group(1)
    # then try to obtain version data from git.
    gitdir = os.path.join(MYDIR, '.git')
    if os.path.exists(gitdir) or 'GIT_DIR' in os.environ:
        try:
            g = gitinfo()
        except OSError:
            pass
    # finally, check and update the active version file
    cp = RawConfigParser()
    cp.read(versioncfgfile)
    d = cp.defaults()
    rewrite = not d or (g['commit'] and (
        g['version'] != d.get('version') or g['commit'] != d.get('commit')))
    if rewrite:
        cp.set('DEFAULT', 'version', g['version'])
        cp.set('DEFAULT', 'commit', g['commit'])
        cp.set('DEFAULT', 'date', g['date'])
        cp.set('DEFAULT', 'timestamp', g['timestamp'])
        cp.write(open(versioncfgfile, 'w'))
    return cp

versiondata = getversioncfg()


def dirglob(d, *patterns):
    from glob import glob
    rv = []
    for p in patterns:
        rv += glob(os.path.join(d, p))
    return rv

# define distribution
setup_args = dict(
    name='dpx.srxplanargui',
    cmdclass=dict(build_py=custom_build_pyc),
    version=versiondata.get('DEFAULT', 'version'),
    namespace_packages=['dpx'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        # define console_scripts here, see setuptools docs for details.
        'console_scripts': ['srxgui = dpx.srxplanargui.srxguiapp:main',
                            ],
    },

    author='Simon J.L. Billinge',
    author_email='sb2896@columbia.edu',
    description='xPDFsuite, a software for PDF transformation and visualization',
    maintainer='Xiaohao Yang',
    maintainer_email='sodestiny1@gmail.com',
    license='see LICENSENOTICE.txt',
    url='',
    keywords='2D powder diffraction image integration uncertainty propagation',
    classifiers=[
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Intended Audience :: Science/Research',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Physics',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)

# End of file
