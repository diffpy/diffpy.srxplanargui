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
import ConfigParser
import re, os, sys
from functools import partial
import argparse


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


from dpx.confutils.configtraits import ConfigBaseTraits
from dpx.confutils.tools import _configPropertyRad, _configPropertyR, _configPropertyRW
from dpx.srxplanar.srxplanarconfig import _description, _epilog, _optdatalist,\
        _defaultdata, checkMax, parseFit2D

class SrXConfig(ConfigBaseTraits):
    '''
    config class, based on ConfigBase class in diffpy.confutils
    '''
    
    # Text to display before the argument help
    _description = _description
    
    # Text to display after the argument help
    _epilog = _epilog

    _optdatalist = _optdatalist
        
    _defaultdata = _defaultdata
    
    rotation = Property(depends_on='rotationd', fget = lambda self: np.radians(self.rotationd))
    tilt = Property(depends_on='tiltd', fget = lambda self: np.radians(self.tiltd))
    tthstep = Property(depends_on='tthstepd', fget = lambda self: np.radians(self.tthstepd))
    tthmax = Property(depends_on='tthmaxd', fget = lambda self: np.radians(self.tthmaxd))
    
    tthorqmax = Property(depends_on='integrationspace, tthmaxd, qmax', 
        fget = lambda self: self.tthmax if self.integrationspace == 'twotheta' else self.qmax)
    tthorqstep = Property(depends_on='integrationspace, tthmaxd, qmax', 
        fget = lambda self: self.tthstep if self.integrationspace == 'twotheta' else self.qstep)
    
    fit2dmask = File('')
    
    def _preUpdateSelf(self, **kwargs):
        '''
        additional process called in self._updateSelf, this method is called
        before self._copySelftoConfig(), i.e. before copy options value to
        self.config (config file)
        
        check the tthmaxd and qmax, and set tthorqmax, tthorqstep according to integration space
        
        :param kwargs: optional kwargs
        '''
        self.tthmaxd, self.qmax = checkMax(self)
        return
    
    def _fit2dconfig_changed(self):
        '''
        load parameters from fit2d calibration information. copy/paste the fit2d calibration 
        results to a txt file. this function will load xbeamcenter, ybeamceter... from the file
        '''
        rv = parseFit2D(filename)
        if len(rv.values())>0:
            for optname in rv.keys():
                setattr(self, optname, rv[optname])
            self.fit2dconfig = ''
            self._updateSelf()
        return
    
    def _fit2dmask_changed(self):
        if os.path.exists(self.fit2dmask):
            if not self.fit2dmask in self.addmask:
                self.addmask.append(self.fit2dmask)
        return
    
    saveconfigbb = Button('Save integration config')
    loadconfigbb = Button('Load integration config')
    
    basic_group = \
        Group(
              Group(Item('configfile'),
                    HGroup(spring,
                           Item('saveconfigbb'),
                           Item('loadconfigbb'),
                           spring,
                           
                           show_labels = False,
                           ),
                    show_border = True,
                    label = 'Configuration'
                    ),
              Group(
                    Item('savedirectory'),
                    Item('addmask'),
                    Item('fit2dmask'),
                    
                    show_border = True,
                    label = 'Files and masks',
                    ),
              Group(Item('integrationspace'),
                    Item('wavelength', visible_when='integrationspace == "qspace"'),
                    Item('xbeamcenter'),
                    Item('ybeamcenter'),
                    Item('distance'),
                    Item('rotationd'), 
                    Item('tiltd'),
                    Item('tthstepd', visible_when='integrationspace == "twotheta"'),
                    Item('qstep', visible_when='integrationspace == "qspace"'),
                    
                    show_border = True,
                    label = 'Geometry parameters'
                    ),
              
              label = 'Basic'
              )
    
    advanced_group = \
        Group(
              Group(Item('uncertaintyenable', label='uncertainty'),
                    Item('sacorrectionenable', label='solid angle corr.'),
                    Item('polcorrectionenable', label='polarization corr.'),
                    Item('polcorrectf', label = 'polarization factor'),
                    
                    show_border = True,
                    label = 'Corrections'
                    ),
              Group(Item('fliphorizontal'),
                    Item('flipvertical'),
                    Item('xdimension'),
                    Item('ydimension'),
                    Item('xpixelsize'),
                    Item('ypixelsize'),
                    Item('maskedges', editor = ArrayEditor(width = -50)),
                    
                    show_border = True,
                    label = 'Detector parameters'
                    ),

              label = 'Advanced'
              )
        
    basic_view = \
        View(basic_group,
             
             resizable = True,
             scrollable = True,
             #handler = handler,
             #icon = ImageResource('icon.ico'),
             )
    advanced_view = \
        View(advanced_group,
             
             resizable = True,
             scrollable = True,
             #handler = handler,
             #icon = ImageResource('icon.ico'),
             )
        
    srx_view = \
        View(
             Group(basic_group,
                   advanced_group,
                   
                   show_labels = False,
                   show_border = True,
                   layout = 'tabbed',
                   #layout = 'split',
                   #orientation = 'horizontal',
                   springy = True,
                   dock = 'tab',
                   ),
             width     = 600,
             height    = 800,
             resizable = True,
             #handler = handler,
             #icon = ImageResource('icon.ico'),
             )
    
SrXConfig.initConfigClass()

if __name__=='__main__':
    a = SrXConfig()
    #a.updateConfig()
    a.configure_traits(view='srx_view')
