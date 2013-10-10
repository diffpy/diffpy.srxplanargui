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
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons
from pyface.api import ImageResource
from enthought.pyface.api import SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanar.srxplanar import SrXplanar

class SrXgui(HasTraits):
    
    addfiles = Instance(AddFiles)
    srxconfig = Instance(SrXconfig)
    splash = Any
    
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
    
    def _integratebb_fired(self):
        self.processSelected(False)
        return
    
    def _integratessbb_fired(self):
        #self.edit_traits(view = 'ssfile_view')
        self.processSelected(True)
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
        
        self.splash.close()
        return
    
    integratebb = Button('Integrate separately')
    integratessbb = Button('Sum and Integrate')
    saveconfigbb = Button('Save integration config')
    loadconfigbb = Button('Load integration config')
    
    
    ssfile_view = \
        View(Item('ssfile', label='file name'),
             
             title = 'save',
             buttons = OKCancelButtons,
             )
            
    traits_view = \
            View(
                 HGroup(Item('addfiles', editor = InstanceEditor(view = 'traits_view'),
                             style = 'custom', label = 'Files'),
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
                 Item('integratebb'),
                 Item('integratessbb'),
                 
                 resizable=True, 
                 title='SrXgui',
                 width=800, 
                 height=700,
                 kind = 'live',
                 icon = ImageResource('icon.ico'),
                 #handler = GetXguiHandler(ddmenu = dropdown_menu),
                 )
            
def main():
    splash = SplashScreen(image=ImageResource('splash.png'))
    splash.open()
    
    gui = SrXgui(splash=splash)
    gui.configure_traits(view = 'traits_view')
    return

if __name__=='__main__':
    sys.exit(main())