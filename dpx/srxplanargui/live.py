#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanar  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSENOTICE.txt for license information.
#
##############################################################################

import numpy as np
import re, os, sys
from functools import partial

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt,\
    HasTraits, Property, Instance, Event, Button, Any, \
    on_trait_change, DelegatesTo, cached_property, property_depends_on
    
from traitsui.api import \
    Item, Group, View, Handler, Controller, spring, Action, \
    HGroup, VGroup, Tabbed, \
    RangeEditor, CheckListEditor, TextEditor, EnumEditor, ButtonEditor, \
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, BooleanEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons
from pyface.api import ImageResource
from enthought.pyface.api import SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanargui.srxgui import SrXgui, SrXguiHandler
from dpx.srxplanar.srxplanar import SrXplanar

from dpx.confutils.tools import checkMD5, checkCRC32

class SrXguiLive(SrXgui):
    
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

    def _startlivebb_changed(self):
        self.capturing = True
        return
    
    def _stoplivebb_changed(self):
        self.capturing = False
        return
    
    capturing = Bool(False)
    startlivebb = Button('Start capturing')
    stoplivebb = Button('Stop capturing')
    
    about_action = \
        Action(name = 'About',
               action = '_aboutmgs')  
    main_group = \
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
               )

    traits_view = \
        View(Group(main_group,
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




def main():
    splash = SplashScreen(image=ImageResource('splash.png'))
    splash.open()
    
    gui = SrXguiLive(splash=splash)
    gui.configure_traits(view = 'traits_view')
    return

if __name__=='__main__':
    sys.exit(main())
    