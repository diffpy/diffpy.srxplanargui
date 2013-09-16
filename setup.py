#!/usr/bin/env python
##############################################################################
#
# dpx.pdfgetxgui    by Simon J. L. Billinge group
#                   (c) 2012 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# Installation script for diffpy.pdfgetx

"""dpx.srxplanargui
"""

from setuptools import setup, find_packages

# define distribution
dist = setup(
        name = 'dpx.srxplanargui',
        version = '0.1',
        namespace_packages = ['dpx'],
        packages = find_packages(),
        include_package_data = True,
        scripts = [],
        data_files = [],
        install_requires = [],
        dependency_links = [],
        entry_points = {
            # define console_scripts here, see setuptools docs for details.
            'console_scripts' : ['srxgui = dpx.srxplanargui.srxgui:main',
                                 'srxplanargui = dpx.srxplanargui.srxgui:main'
                                 ],
        },

        author = 'Simon J.L. Billinge',
        author_email = 'sb2896@columbia.edu',
        description = 'GUI for SrXplanar, a program integrate 2D diffraction image.',
        license = 'BSD',
        #url = 'http://www.diffpy.org/',
        keywords = 'PDF x-ray Fourier transform',
)

# End of file
