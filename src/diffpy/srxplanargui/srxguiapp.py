#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanargui    by Simon J. L. Billinge group
#                   (c) 2012-2025 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Provide UI for srxplanar."""

import logging
import os
import sys
import warnings

from pyface.api import ImageResource, SplashScreen
from traits.etsconfig.api import ETSConfig

from diffpy.srxplanargui.srxgui import SrXgui

warnings.filterwarnings("ignore")


logging.disable("CRITICAL")

# break if help passed to the args
sysargv = sys.argv[1:]
if ("--help" in sysargv) or ("-h" in sysargv):
    from diffpy.srxplanargui.srxconfig import SrXconfig

    SrXconfig(args=sysargv)


os.environ["QT_API"] = "pyside"
ETSConfig.toolkit = "qt"


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
