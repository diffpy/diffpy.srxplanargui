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

from dpx.srxplanargui.selectfiles import AddFiles
from diffpy.srxplanar.srxplanar import SrXplanar
from diffpy.srxplanar.srxplanarconfig import SrXplanarConfig

class SrXgui(HasTraits):
    
    addfiles = Instance(AddFiles)
    
    savedirectory = Directory(os.getcwd())
    addmask = List(['edgemask'])
    fit2dmask = File()
    
    integrationspace = Enum(['qspace', 'twotheta'])
    wavelength = Float(0.1)
    xbeamcenter = Float(1024.0)
    ybeamcenter = Float(1024.0)
    distance = Float(200.0)
    rotationd = Float(0.0) 
    tiltd = Float(0.0)
    tthstepd = Float(0.02)
    qstep = Float(0.02)
    
    fliphorizontal = Bool(False)
    flipvertical = Bool(True)
    xdimension = Int(2048)
    ydimension = Int(2048)
    xpixelsize = Float(0.2)
    ypixelsize = Float(0.2)
    
    uncertaintyenable = Bool(True)
    sacorrectionenable = Bool(True)
    polcorrectionenable = Bool(True)
    polcorrectf = Float(0.95)
    selfcorrenable = Bool(True)
    maskedges = Array()
    
    
    def _maskedges_default(self):
        return np.array([20,20,20,20,100])
    
    def applyConfig(self):
        if os.path.exists(self.fit2dmask):
            if not self.fit2dmask in self.addmask:
                self.addmask.append(self.fit2dmask)
        
        conflist = ['savedirectory','addmask', 'integrationspace', 'wavelength', 'xbeamcenter',
                    'ybeamcenter', 'distance', 'rotationd', 'tiltd', 'tthstepd', 'qstep',
                    'fliphorizontal', 'flipvertical', 'xdimension', 'ydimension', 'xpixelsize',
                    'ypixelsize', 'uncertaintyenable', 'sacorrectionenable', 'polcorrectionenable',
                    'polcorrectf', 'selfcorrenable' ,'maskedges']
        
        for conf in conflist:
            setattr(self.srxconfig, conf, getattr(self, conf))
        self.srxconfig.updateConfig()
        return
    
    ssfile = File
    def processSelected(self, ss=False):
        if self.addfiles.selected:
            self.applyConfig()
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
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
    
    def __init__(self):
        '''
        init the object, createt the notifications
        '''
        super(SrXgui, self).__init__()
        self.addfiles = AddFiles()
        self.srxconfig = SrXplanarConfig()
        self.srx = SrXplanar(self.srxconfig)
        return
    
    integratebb = Button('Integrate separately')
    integratessbb = Button('Sum and Integrate')
    
    basic = \
        Group(
              Group(
                    Item('savedirectory'),
                    Item('addmask'),
                    Item('fit2dmask'),
                    Item('integrationspace'),
                    
                    show_border = True
                    ),
              Group(Item('wavelength', visible_when='integrationspace == "qspace"'),
                    Item('xbeamcenter'),
                    Item('ybeamcenter'),
                    Item('distance'),
                    Item('rotationd'), 
                    Item('tiltd'),
                    Item('tthstepd', visible_when='integrationspace == "twotheta"'),
                    Item('qstep', visible_when='integrationspace == "qspace"'),
                    
                    show_border = True,
                    ),
              HGroup(spring,
                     Item('integratebb'),
                     Item('integratessbb'),
                     spring,
                     
                     show_labels = False,
                     ),
              label = 'Basic'
              )
    
    advanced = \
        Group(
              Group(Item('uncertaintyenable', label='uncertainty'),
                    Item('sacorrectionenable', label='solid angle corr.'),
                    Item('polcorrectionenable', label='polarization corr.'),
                    Item('polcorrectf', label = 'polarization factor'),
                    Item('selfcorrenable', label = 'self corr.'),
                    
                    show_border = True,
                    ),
              Group(Item('fliphorizontal'),
                    Item('flipvertical'),
                    Item('xdimension'),
                    Item('ydimension'),
                    Item('xpixelsize'),
                    Item('ypixelsize'),
                    Item('maskedges', editor = ArrayEditor(width = -50)),
                    
                    show_border = True,
                    ),
              HGroup(spring,
                     Item('integratebb'),
                     Item('integratessbb'),
                     spring,
                     
                     show_labels = False,
                     ),
              label = 'Advanced'
              )
    
    ssfile_view = \
        View(Item('ssfile', label='file name'),
             
             title = 'save',
             buttons = OKCancelButtons,
             )
    
    traits_view = \
            View(
                 HGroup(Item('addfiles', editor = InstanceEditor(view = 'traits_view'),
                             style = 'custom'),
                        Tabbed(basic,
                               advanced
                               ),

                       layout = 'split',
                       #springy = True,
                       dock = 'tab',
                       show_labels = False
                       ),
                 resizable=True, 
                 title='SrXplanar GUI',
                 width=800, 
                 height=600,
                 kind = 'live',
                 #menubar = menu1,
                 )
            
def main():
    gui = SrXgui()
    gui.configure_traits(view = 'traits_view')
    return

if __name__=='__main__':
    sys.exit(main())