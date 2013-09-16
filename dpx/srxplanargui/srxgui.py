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
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar
from pyface.api import ImageResource

from dpx.srxplanargui.selectfiles import AddFiles


class SrXgui(GetX):
    
    addfiles = Instance(AddFiles)
    
    savedirectory = Directory(os.getcwd())
    addmask = List(['edgemask'])
    fit2dmask = File()
    
    integrationspace = Enum(['qspace', 'twotheta'])
    wavelength = Float(0.1)
    xbeamcenter = Float(1024.0)
    ybeamcenter = Float(1024.0)
    distance = Float(200.0)
    rotationd = 
    tiltd
    tthstepd
    qstep
    
    fliphorizontal
    flipvertical
    xdimension
    ydimension
    xpixelsize
    ypixelsize
    
    uncertaintyenable
    sacorrectionenable
    polcorrectionenable
    polcorrectf
    selfcorrenable
    maskedges
    
    
    
    def __init__(self):
        '''
        init the object, createt the notifications
        '''
        super(SrXgui, self).__init__()
        return
    
    traits_view = \
            View(
                 HGroup(Item('selectfiles', editor = InstanceEditor(view = 'traits_view'),
                             style = 'custom', width=220),

                       layout = 'split',
                       springy = True,
                       dock = 'tab',
                       show_labels = False
                       ),
                 resizable=True, 
                 title='SrXplanar GUI',
                 width=700, 
                 height=600,
                 kind = 'live',
                 toolbar = toolbar,
                 #menubar = menu1,
                 handler = GetXguiHandler(ddmenu = dropdown_menu)
                 )
            
def main():
    gui = SrXgui(args=sys.argv[1:])
    gui.configure_traits(view = 'traits_view')
    return

if __name__=='__main__':
    sys.exit(main())