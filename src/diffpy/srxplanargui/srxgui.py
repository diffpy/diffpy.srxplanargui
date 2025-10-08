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

from pyface.api import ImageResource
from traits.api import Any, Button, File, HasTraits, Instance
from traits.etsconfig.api import ETSConfig
from traitsui.api import (
    Action,
    Group,
    Handler,
    HGroup,
    InstanceEditor,
    Item,
    VGroup,
    View,
    spring,
)
from traitsui.menu import CancelButton, OKButton

from diffpy.srxplanar.srxplanar import SrXplanar
from diffpy.srxplanargui.calibration import Calibration
from diffpy.srxplanargui.help import SrXguiHelp
from diffpy.srxplanargui.selectfiles import AddFiles
from diffpy.srxplanargui.srxconfig import SrXconfig

ETSConfig.toolkit = "qt"


class SrXguiHandler(Handler):

    def closed(self, info, is_ok):
        """Notify main gui to delete current plot in plots list."""
        configfile = info.object.detectConfigfile("default")
        info.object.saveConfig(configfile)
        return True

    def _saveconfigView(self, info):
        info.object._saveconfigView()
        return

    def _loadconfigView(self, info):
        info.object._loadconfigView()
        return

    def _helpView(self, info):
        info.object._helpbb_changed()
        return


class SaveHandler(Handler):

    def closed(self, info, is_ok):
        if is_ok:
            info.object.saveConfig(info.object.configfile)
        return True


class LoadHandler(Handler):
    def closed(self, info, is_ok):
        if is_ok:
            info.object.loadConfig(info.object.configfile)
        return


class SrXgui(HasTraits):

    addfiles = Instance(AddFiles)
    srxconfig = Instance(SrXconfig)
    help = Instance(SrXguiHelp)
    splash = Any
    calibration = Instance(Calibration)

    def __init__(self, configfile=None, args=None, **kwargs):
        """Init the object, createt the notifications."""
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

        # self.loadConfig(configfile)
        self.splash.close()
        return

    def saveConfig(self, filename=None):
        """Save config."""
        if filename == "default":
            filename = self.detectConfigfile(filename)
        self.srxconfig.writeConfig(filename, mode="full")
        self.configfile = filename
        return

    def loadConfig(self, filename=None):
        """Load config."""
        configfile = self.detectConfigfile(filename)
        if os.path.exists(configfile):
            self.srxconfig.updateConfig(filename=configfile)
            self.configfile = configfile
        return

    def processSelected(self, summation=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            self.srx.prepareCalculation(filelist)
            self.srx.integrateFilelist(filelist, summation=summation)
        return

    def detectConfigfile(self, filename):
        """Current directory > home directory, if none, then return the
        curdir+filename if 'default', then return home+filename."""
        if filename is None:
            configfile = os.path.join(os.path.curdir, "srxconfig.cfg")
        elif filename == "default":
            configfile = os.path.join(os.path.expanduser("~"), "srxconfig.cfg")
        else:
            if os.path.abspath(filename):
                if os.path.exists(filename):
                    configfile = filename
                else:
                    filename = os.path.split(filename)[1]
                    configfile = os.path.join(os.path.curdir, filename)
            else:
                configfile = os.path.join(os.path.curdir, filename)
        return configfile

    ###########################################################
    def _saveconfigView(self):
        self.edit_traits(view="saveconfig_view")
        return

    def _loadconfigView(self):
        self.edit_traits(view="loadconfig_view")
        return

    configfile = File()
    helpbutton_action = Action(name="Help ", action="_helpView")
    saveconfig_action = Action(name="Save Config", action="_saveconfigView")
    loadconfig_action = Action(name="Load Config", action="_loadconfigView")

    saveconfig_view = View(
        Item("configfile"),
        resizable=True,
        title="Save config",
        width=500,
        buttons=[OKButton, CancelButton],
        handler=SaveHandler(),
        icon=ImageResource("icon.png"),
    )
    loadconfig_view = View(
        Item("configfile"),
        resizable=True,
        title="Load config",
        width=500,
        buttons=[OKButton, CancelButton],
        handler=LoadHandler(),
        icon=ImageResource("icon.png"),
    )
    #############################################################

    def _integratbb_changed(self):
        self.processSelected(False)
        return

    def _integratessbb_changed(self):
        self.processSelected(True)
        return

    def _helpbb_changed(self):
        self.help.edit_traits(view="quickstart_view")
        return

    def _selfcalibratebb_changed(self):
        image = None
        if self.addfiles.selected is not None:
            if len(self.addfiles.selected) == 1:
                image = self.addfiles.selected[0].fullname

        if image is not None:
            self.calibration.image = image
        self.calibration.edit_traits(view="main_View")
        return

    integratbb = Button("Integrate")
    integratessbb = Button("Sum and Integrate")
    selfcalibratebb = Button("Calibrate")
    helpbb = Button("Help")

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
                    Item("selfcalibratebb"),
                    Item("integratbb"),
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
        buttons=[
            helpbutton_action,
            saveconfig_action,
            loadconfig_action,
            OKButton,
        ],
        icon=ImageResource("icon.png"),
        handler=SrXguiHandler(),
    )


if __name__ == "__main__":
    sys.exit()
