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

'''provide UI for srxplanar
'''

import numpy as np
import os
import sys

import warnings
warnings.filterwarnings("ignore")

# break if help passed to the args
sysargv = sys.argv[1:]
if ('--help' in sysargv) or('-h' in sysargv):
    from dpx.srxplanargui.srxconfig import SrXconfig
    SrXconfig(args=sysargv)

from traits.etsconfig.api import ETSConfig
if any([aa == 'wx' for aa in sysargv]):
    ETSConfig.toolkit = 'wx'
    import wx
    import traitsui.wx.constants
    traitsui.wx.constants.WindowColor = wx.Colour(244, 243, 238)
else:
    os.environ['QT_API'] = 'pyside'
    ETSConfig.toolkit = 'qt4'
    from pyface.qt import QtGui, QtCore

from pyface.api import ImageResource, SplashScreen
# open splash screen
splash = SplashScreen(image=ImageResource('01.png'), show_log_messages=False)
if not any([aa == '-h' or aa == '--help' for aa in sysargv]):
    splash.open()

from dpx.srxplanargui.srxgui import SrXgui

def main():
    gui = SrXgui(splash=splash)
    gui.configure_traits(view='traits_view')
    return

if __name__ == '__main__':
    sys.exit(main())
