#!/usr/bin/env python

# Installation script for dpx.pdfgetxgui

"""dpx.srxplanargui - a software for 2D powder diffraction image integration
    and error propagation

Packages:   dpx.srxplanargui
Scripts:    srxgui
"""

import os
import glob
from setuptools import setup, find_packages

# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, 'dpx', 'srxplanargui', 'version.cfg')
defaultversion = '1.0_tem'

def gitinfo():
    from subprocess import Popen, PIPE
    kw = dict(stdout=PIPE, cwd=MYDIR)
    rv = {}
    proc = Popen(['git', 'describe', '--match=v[[:digit:]]*'], **kw)
    desc = proc.stdout.read()
    proc = Popen(['git', 'log', '-1', '--format=%H %at %ai'], **kw)
    glog = proc.stdout.read()
    if desc != '':
        rv['version'] = desc.strip().split('-')[0].lstrip('v')
    else:
        rv['version'] = defaultversion
    if glog != '':
        rv['commit'], rv['timestamp'], rv['date'] = glog.strip().split(None, 2)
    else:
        rv['commit'], rv['timestamp'], rv['date'] = 'no git', 'no git', 'no git'
    return rv


def getversioncfg():
    from ConfigParser import SafeConfigParser
    cp = SafeConfigParser()
    cp.read(versioncfgfile)
    gitdir = os.path.join(MYDIR, '.git')
    if not os.path.isdir(gitdir):
        # not a git repo
        cp.set('DEFAULT', 'version', defaultversion)
        cp.set('DEFAULT', 'commit', 'no git')
        cp.set('DEFAULT', 'date', 'no git')
        cp.set('DEFAULT', 'timestamp', 'no git')
        cp.write(open(versioncfgfile, 'w'))
    try:
        g = gitinfo()
    except OSError:
        return cp
    d = cp.defaults()
    if g['version'] != d.get('version') or g['commit'] != d.get('commit'):
        cp.set('DEFAULT', 'version', g['version'])
        cp.set('DEFAULT', 'commit', g['commit'])
        cp.set('DEFAULT', 'date', g['date'])
        cp.set('DEFAULT', 'timestamp', g['timestamp'])
        cp.write(open(versioncfgfile, 'w'))
    return cp

versiondata = getversioncfg()

# define distribution
setup_args = dict(
        name='dpx.srxplanargui',
        version=versiondata.get('DEFAULT', 'version'),
        namespace_packages=['dpx'],
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        entry_points={
            # define console_scripts here, see setuptools docs for details.
            'console_scripts' : ['srxgui = dpx.srxplanargui.srxguiapp:main',
                                 ],
        },

        author='Simon J.L. Billinge',
        author_email='sb2896@columbia.edu',
        description='PDFgetXgui, a software for PDF transformation and visualization',
        maintainer='Xiaohao Yang',
        maintainer_email='xiaohao.yang@outlook.com',
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
