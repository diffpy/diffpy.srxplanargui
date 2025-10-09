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

import os
import sys

from pyface.api import GUI, ImageResource, SplashScreen
from traits.api import Any, on_trait_change
from traits.etsconfig.api import ETSConfig
from traitsui.api import (
    Action,
    Group,
    HGroup,
    InstanceEditor,
    Item,
    VGroup,
    View,
    spring,
)
from traitsui.menu import OKButton

from diffpy.srxplanar.srxplanar import SrXplanar
from diffpy.srxplanargui.calibration import Calibration
from diffpy.srxplanargui.help import SrXguiHelp
from diffpy.srxplanargui.selectfiles import AddFiles
from diffpy.srxplanargui.srxconfig import SrXconfig
from diffpy.srxplanargui.srxgui import SrXgui, SrXguiHandler

ETSConfig.toolkit = "qt"


class SrXguiLive(SrXgui):

    getxgui = Any

    def __init__(self, configfile=None, args=None, **kwargs):

        # init the object, createt the notifications

        self.splash = SplashScreen(
            image=ImageResource("01.png"), show_log_messages=False
        )
        self.splash.open()

        super(SrXgui, self).__init__(**kwargs)
        configfile = self.detectConfigfile(configfile)
        if not os.path.exists(configfile):
            configfile = self.detectConfigfile("default")
        self.configfile = configfile

        if not kwargs.has_key("srxconfig"):
            self.srxconfig = SrXconfig(
                filename=configfile, args=args, **kwargs
            )

        self.addfiles = AddFiles(srxconfig=self.srxconfig)
        self.srx = SrXplanar(self.srxconfig)
        self.addfiles.srx = self.srx
        self.help = SrXguiHelp()
        self.calibration = Calibration(srx=self.srx, srxconfig=self.srxconfig)
        self.splash.close()
        return

    @on_trait_change("srxconfig.savedirectory")
    def _changedir(self):
        newdir = self.srxconfig.savedirectory
        if os.path.exists(newdir):
            self.getxgui.getxconfig.inputdir = os.path.abspath(newdir)
            self.getxgui.getxconfig.savedir = os.path.abspath(newdir)
        else:
            self.getxgui.getxconfig.inputdir = os.path.abspath(os.path.curdir)
            self.getxgui.getxconfig.savedir = os.path.abspath(os.path.curdir)
        return

    def processSelected(self, summation=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            self.srx.prepareCalculation(filelist)
            rvlist = self.srx.integrateFilelist(filelist, summation=summation)
            newchifilelist = [rv["filename"] for rv in rvlist]
            GUI.invoke_later(self.addNewImagesToGetXgui, newchifilelist)
        return

    def addNewImagesToGetXgui(self, filelist):
        """Add new images to getxgui, if images are already there,
        refresh them.

        :param filelist: list of full path of new images
        """
        self.addfiles.refreshdatalist = True
        newdatacontainers = self.getxgui.selectfiles.addFiles(filelist)
        self.getxgui.createNewPlot(newdatacontainers)
        return

    helpbutton_action = Action(name="Help ", action="_helpView")
    saveconfig_action = Action(
        name="Save Config",
        action="_saveconfigView",
        enabled_when="not capturing",
    )
    loadconfig_action = Action(
        name="Load Config",
        action="_loadconfigView",
        enabled_when="not capturing",
    )

    traits_view = View(
        HGroup(
            Item(
                "addfiles",
                editor=InstanceEditor(view="traits_view"),
                style="custom",
                label="Files",
                width=0.4,
            ),
            VGroup(
                Group(
                    Item(
                        "srxconfig",
                        editor=InstanceEditor(view="main_view"),
                        style="custom",
                        label="Basic",
                        show_label=False,
                    ),
                    springy=True,
                ),
                HGroup(
                    spring,
                    Item("selfcalibratebb", enabled_when="not capturing"),
                    Item("integratbb", enabled_when="not capturing"),
                    spring,
                    show_labels=False,
                ),
            ),
            layout="split",
            springy=True,
            dock="tab",
            show_labels=False,
        ),
        resizable=True,
        title="SrXgui",
        width=700,
        height=650,
        kind="live",
        icon=ImageResource("icon.png"),
        handler=SrXguiHandler(),
        buttons=[
            helpbutton_action,
            saveconfig_action,
            loadconfig_action,
            OKButton,
        ],
    )


def main():
    gui = SrXguiLive()
    gui.configure_traits(view="traits_view")
    return


if __name__ == "__main__":
    sys.exit(main())
