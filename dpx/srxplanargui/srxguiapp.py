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
"""Provide UI for srxplanar."""

import os
import sys
import warnings

import numpy as np
from pyface.api import ImageResource, SplashScreen
from pyface.qt import QtCore, QtGui
from traits.etsconfig.api import ETSConfig

from dpx.srxplanargui.srxgui import SrXgui

warnings.filterwarnings("ignore")
import logging

logging.disable("CRITICAL")

# break if help passed to the args
sysargv = sys.argv[1:]
if ("--help" in sysargv) or ("-h" in sysargv):
    from dpx.srxplanargui.srxconfig import SrXconfig

    SrXconfig(args=sysargv)


os.environ["QT_API"] = "pyside"
ETSConfig.toolkit = "qt4"

# open splash screen
splash = SplashScreen(image=ImageResource("01.png"), show_log_messages=False)
if not any([aa == "-h" or aa == "--help" for aa in sysargv]):
    splash.open()


def main():
    gui = SrXgui(splash=splash)
    gui.configure_traits(view="traits_view")
    return


if __name__ == "__main__":
    sys.exit(main())
