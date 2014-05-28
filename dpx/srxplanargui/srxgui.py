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
    ETSConfig.toolkit = 'qt4'
    from pyface.qt import QtGui, QtCore

from pyface.api import ImageResource, SplashScreen
# open splash screen
splash = SplashScreen(image=ImageResource('01.png'))
if not any([aa == '-h' or aa == '--help' for aa in sysargv]):
    splash.open()

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt, \
    HasTraits, Property, Instance, Event, Button, Any, \
    on_trait_change, DelegatesTo, cached_property, property_depends_on

from traitsui.api import \
    Item, Group, View, Handler, Controller, spring, Action, \
    HGroup, VGroup, Tabbed, \
    RangeEditor, CheckListEditor, TextEditor, EnumEditor, ButtonEditor, \
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, ImageEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from diffpy.srxplanar.srxplanar import SrXplanar
from dpx.srxplanargui.help import SrXguiHelp
from dpx.srxplanargui.calibration import Calibration

class SrXguiHandler(Handler):

    def closed(self, info, is_ok):
        '''
        notify main gui to delete current plot in plots list
        '''
        info.object.saveConfig('default')
        return True

    def _quickstart(self, info):
        info.object._helpbb_changed()
        return
    
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
        '''
        init the object, createt the notifications
        '''
        super(SrXgui, self).__init__(**kwargs)
        configfile = self.detectConfigfile(configfile)
        if not os.path.exists(configfile):
            configfile = self.detectConfigfile('default')
        self.configfile = configfile
        
        if not kwargs.has_key('srxconfig'):
            self.srxconfig = SrXconfig(filename=configfile, args=args, **kwargs)

        self.addfiles = AddFiles(srxconfig=self.srxconfig)
        self.srx = SrXplanar(self.srxconfig)
        self.help = SrXguiHelp()
        self.calibration = Calibration(srx=self.srx, srxconfig=self.srxconfig)

        # self.loadConfig(configfile)
        self.splash.close()
        return


    def saveConfig(self, filename=None):
        '''
        save config
        '''
        # configfile = self.detectConfigfile(filename)
        self.srxconfig.writeConfig(filename, mode='full')
        self.configfile = filename  
        return

    def loadConfig(self, filename=None):
        '''
        load config
        '''
        configfile = self.detectConfigfile(filename)
        if os.path.exists(configfile):
            self.srxconfig.updateConfig(filename=configfile)
            self.configfile = configfile
        return

    def processSelected(self, ss=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            self.srx.prepareCalculation(filelist)
            if ss:
                self.srx.integrateFilelist(filelist, summation=True)
            else:
                self.srx.integrateFilelist(filelist, summation=False)
        return
    
    def detectConfigfile(self, filename):
        '''
        current directory > home directory, if none, then return the curdir+filename
        if 'default', then return home+filename
        '''
        if filename == None:
            configfile = os.path.join(os.path.curdir, 'srxconfig.cfg')
        elif filename == 'default':
            configfile = os.path.join(os.path.expanduser('~'), 'srxconfig.cfg')    
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
        self.edit_traits(view='saveconfig_view')
        return
    def _loadconfigView(self):
        self.edit_traits(view='loadconfig_view')
        return
    
    configfile = File()
    savebutton_action = \
        Action(name='Save Config',
               action='_saveconfigView')
    loadbutton_action = \
        Action(name='Load Config',
               action='_loadconfigView')

    saveconfig_view = \
            View(Item('configfile'),

                 resizable=True,
                 title='Save config',
                 width=500,
                 buttons=[OKButton, CancelButton],
                 handler=SaveHandler(),
                 icon=ImageResource('icon.ico'),
                 )
    loadconfig_view = \
            View(Item('configfile'),

                 resizable=True,
                 title='Load config',
                 width=500,
                 buttons=[OKButton, CancelButton],
                 handler=LoadHandler(),
                 icon=ImageResource('icon.ico'),
                 )
    #############################################################

    def _integratbb_changed(self):
        self.processSelected(False)
        return

    def _integratessbb_changed(self):
        self.processSelected(True)
        return

    def _helpbb_changed(self):
        self.help.edit_traits(view='quickstart_view')
        return
    
    def _selfcalibratebb_changed(self):
        image = None
        if self.addfiles.selected != None:
            if len(self.addfiles.selected) == 1:
                image = self.addfiles.selected[0].fullname
        
        if image != None:
            self.calibration.image = image
        self.calibration.edit_traits(view='main_View')
        return
    
    helpbutton_action = \
        Action(name='Help ',
               action='_helpView')

    integratbb = Button('Integrate separately')
    integratessbb = Button('Sum and Integrate')
    selfcalibratebb = Button('Calibration')
    helpbb = Button('Help')
        
    calibrate_view = \
        View(Item('srxconfig'),
             # Item('srxconfig', editor=InstanceEditor(view='calibrate_view'),
             #     style='custom'),
             width=600,
             height=200,
             resizable=True,
             # handler = handler,
             icon=ImageResource('icon.ico'),
             )
        
    traits_view = \
        View(
            HGroup(
                Item('addfiles', editor=InstanceEditor(view='traits_view'),
                     style='custom', label='Files', width=0.4),
                VGroup(
                    Group(Item('srxconfig', editor=InstanceEditor(view='main_view'),
                               style='custom', label='Basic', show_label=False),
                          # layout='tabbed',
                          springy=True,
                          ),
                    HGroup(spring,
                           Item('selfcalibratebb'),
                           Item('integratbb'),
                           Item('integratessbb'),
                           spring,
                           show_labels=False,
                           ),
                    ),
                   
                   layout='split',
                   springy=True,
                   dock='tab',
                   show_labels=False
                   ),
             resizable=True,
             title='SrXgui',
             width=700,
             height=600,
             kind='live',
             buttons=[helpbutton_action, savebutton_action, loadbutton_action, OKButton],
             icon=ImageResource('icon.ico'),
             handler=SrXguiHandler(),
             )

def main():
    gui = SrXgui(splash=splash)
    gui.configure_traits(view='traits_view')
    return

if __name__ == '__main__':
    sys.exit(main())
