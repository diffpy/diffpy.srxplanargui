#!/usr/bin/env python

"""dpx.srxplanargui
"""

from setuptools import setup, find_packages

# define distribution
dist = setup(
        name='dpx.srxplanargui',
        version='1.0',
        namespace_packages=['dpx'],
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        scripts=[],
        data_files=[],
        install_requires=[],
        dependency_links=[],
        entry_points={
            # define console_scripts here, see setuptools docs for details.
            'console_scripts' : ['srxgui = dpx.srxplanargui.srxguiapp:main',
                                 'srxplanargui = dpx.srxplanargui.srxguiapp:main'
                                 ],
        },

        author='Simon J.L. Billinge',
        author_email='sb2896@columbia.edu',
        description='GUI for SrXplanar, a program integrate 2D diffraction image.',
        license='BSD',
        # url = 'http://www.diffpy.org/',
        keywords='PDF x-ray Fourier transform',
)

# End of file
