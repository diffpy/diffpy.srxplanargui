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

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt,\
    HasTraits, Property, Instance, Event, Button, Any, \
    on_trait_change, DelegatesTo, cached_property, property_depends_on

from traitsui.api import \
    Item, Group, View, Handler, Controller, spring, Action, \
    HGroup, VGroup, Tabbed, \
    RangeEditor, CheckListEditor, TextEditor, EnumEditor, ButtonEditor, \
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, ImageEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons
from pyface.api import ImageResource
from enthought.pyface.api import SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanar.srxplanar import SrXplanar

class SrXguiHandler(Handler):
    
    def closed(self, info, is_ok):
        '''
        notify main gui to delete current plot in plots list
        '''
        info.object.saveConfig('default')
        return True
    
    def _aboutmgs(self, info):
        info.object.edit_traits(view = "about_view")
        return
    
class SrXgui(HasTraits):
    
    addfiles = Instance(AddFiles)
    srxconfig = Instance(SrXconfig)
    splash = Any
    
    def saveConfig(self, filename=None):
        '''
        save config
        '''
        configfile = os.path.join(os.path.expanduser('~'), 'srxconfig.cfg')
        if filename == None:
            if os.path.exists(self.srxconfig.configfile): 
                configfile = self.srxconfig.configfile
        else:
            if filename != 'default':
                configfile = filename
        self.srxconfig.writeConfig(configfile, mode='full')
        return
    
    def loadConfig(self, filename=None):
        '''
        load config
        '''
        configfile = os.path.join(os.path.expanduser('~'), 'srxconfig.cfg')
        if filename == None:
            if os.path.exists(self.srxconfig.configfile): 
                configfile = self.srxconfig.configfile
        else:
            if os.path.exists(filename):
                configfile = filename
        
        if os.path.exists(configfile):
            self.srxconfig.updateConfig(filename = configfile)
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
    
    def __init__(self, configfile=None, args=None, **kwargs):
        '''
        init the object, createt the notifications
        '''
        super(SrXgui, self).__init__(configfile=None, args=None, **kwargs)
        if not kwargs.has_key('srxconfig'):
            self.srxconfig = SrXconfig(filename = configfile, args=args, **kwargs)

        self.addfiles = AddFiles(srxconfig = self.srxconfig)
        self.srx = SrXplanar(self.srxconfig)
        
        self.loadConfig('default')
        self.splash.close()
        return
    
    def _integratbb_changed(self):
        self.processSelected(False)
        return
    
    def _integratessbb_changed(self):
        self.processSelected(True)
        return
    
    def _startlivebb_changed(self):
        self.capturing = True
        return
    
    def _stoplivebb_changed(self):
        self.capturing = False
        return
    
    about_action = \
        Action(name = 'About',
               action = '_aboutmgs')
    
    integratbb = Button('Integrate separately')
    integratssbb = Button('Sum and Integrate')
    
    capturing = Bool(False)
    startlivebb = Button('Start capturing')
    stoplivebb = Button('Stop capturing')
    
    saveconfigbb = Button('Save')
    loadconfigbb = Button('Load')
            
    traits_view = \
            View(
                Group(
                     HGroup(Item('addfiles', editor = InstanceEditor(view = 'traits_view'),
                                 style = 'custom', label = 'Files', width=0.4),
                            Group(Item('srxconfig', editor = InstanceEditor(view = 'basic_view'), 
                                       style = 'custom', label='Basic', show_label = False),
                                  Item('srxconfig', editor = InstanceEditor(view = 'advanced_view'), 
                                       style = 'custom', label='Advanced', show_label = False),
                                  layout = 'tabbed',
                                  springy = True,
                                  ),
                           layout = 'split',
                           springy = True,
                           dock = 'tab',
                           show_labels = False
                           ),
                      HGroup(spring,
                             Item('integratbb'),
                             Item('integratssbb'),
                             spring,
                             Item('startlivebb', enabled_when='capturing == False'),
                             Item('stoplivebb', enabled_when='capturing == True'),
                             spring,
                             
                             show_labels = False,
                             ),
                      ),
                 
                 resizable=True, 
                 title='SrXgui',
                 width=800, 
                 height=700,
                 kind = 'live',
                 icon = ImageResource('icon.ico'),
                 handler = SrXguiHandler(),
                 buttons = [OKButton, about_action],
                 )
            
    qsimage = ImageResource('splash.png')
    
    about_view = \
        View(Item('qsimage', editor = ImageEditor(), width = 0.5, show_label=False),
             title = 'Quick start',
             width = 960,
             height = 520, 
             resizable = True,
             buttons = [OKButton],
             icon = ImageResource('icon.ico'),
             )
            
def main():
    splash = SplashScreen(image=ImageResource('splash.png'))
    splash.open()
    
    gui = SrXgui(splash=splash)
    gui.configure_traits(view = 'traits_view')
    return

if __name__=='__main__':
    sys.exit(main())