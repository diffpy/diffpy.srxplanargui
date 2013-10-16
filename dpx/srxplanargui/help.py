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

'''provide help for SrXgui
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
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, \
    ImageEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu

from pyface.api import ImageResource

class HelpHandler(Handler):
    
    def _qsnext(self, info):
        info.object.qsindex += 1
        return
    
    def _qsprevious(self, info):
        info.object.qsindex -= 1
        return
        

class SrXguiHelp(HasTraits):
    
    aboutmsg = Str
    def _aboutmsg_default(self):
        rv = \
'''
PDFGetXgui:
by Simon J. L. Billinge group (c) 2012 Trustees of the Columbia University
in the City of New York.  All rights reserved.

PDFGetX3 coded by:  Pavol Juhas, Timur Davis, Christopher Farrow
PDFGetXgui coded by:  Xiaohao Yang
SrXplanar and SrXgui coded by:  Xiaohao Yang

This program is only to be used by members of the Billinge Group or people that
have otherwise been allowed by the Billinge Group. You can't distribute this
program or use it for commercial or academic use without the express consent of
the Billinge Group.
'''
        return rv
    
    about_view = \
        View(Item('aboutmsg', style='readonly', show_label=False),
             
             title = 'About',
             width = 600,
             buttons = [OKButton],
             icon = ImageResource('icon.ico'),
             )
    
    #######################
    # quick start
    #######################
    
    imgs = [ImageResource('%d.PNG'%i) for i in range(1, 3)]
    
    qslen = Int(1)
    
    next_action = \
        Action(name = 'Next',
               action = '_qsnext',
               enabled_when = 'object.qsindex<object.qslen'
               )
    previous_action = \
        Action(name = 'Previous',
               action = '_qsprevious',
               enabled_when = 'object.qsindex>0'
               )
        
    def _qsnext(self):
        self.qsindex += 1
        return
    def _qsprevious(self):
        self.qsindex -= 1
        return
        
    qsimage = Property
    @property_depends_on('qsindex')
    def _get_qsimage(self):
        return self.imgs[self.qsindex]
    
    qsindex = Int(0)
    quickstart_view = \
        View(Item('qsimage', editor = ImageEditor(), width = 0.5, show_label=False),
             title = 'Quick start',
             width = 980,
             height = 550, 
             resizable = True,
             buttons = [previous_action, next_action, OKButton],
             handler = HelpHandler(),
             icon = ImageResource('icon.ico'),
             )
    