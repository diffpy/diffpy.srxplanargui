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

from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit == 'qt4'

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt, \
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
from diffpy.srxplanar.srxplanarconfig import _description, _epilog, _optdatalist, \
        _defaultdata, checkMax, parseFit2D

class CalibrationHandler(Handler):
    
    def close (self, info, is_ok):
        info.object.calibrationflag = is_ok
        return True

class SrXconfig(ConfigBaseTraits):
    '''
    config class, based on ConfigBase class in diffpy.confutils
    '''

    # Text to display before the argument help
    _description = _description

    # Text to display after the argument help
    _epilog = _epilog

    _optdatalist = _optdatalist

    _defaultdata = {'configfile': [],
                    'headertitle': 'SrXgui configration'
                    }

    rotation = Property(depends_on='rotationd', fget=lambda self: np.radians(self.rotationd))
    tilt = Property(depends_on='tiltd', fget=lambda self: np.radians(self.tiltd))
    tthstep = Property(depends_on='tthstepd', fget=lambda self: np.radians(self.tthstepd))
    tthmax = Property(depends_on='tthmaxd', fget=lambda self: np.radians(self.tthmaxd))

    tthorqmax = Property(depends_on='integrationspace, tthmaxd, qmax',
        fget=lambda self: self.tthmax if self.integrationspace == 'twotheta' else self.qmax)
    tthorqstep = Property(depends_on='integrationspace, tthmaxd, qmax',
        fget=lambda self: self.tthstep if self.integrationspace == 'twotheta' else self.qstep)

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
        if len(rv.values()) > 0:
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

    def _opendirectory_changed(self):
        newdir = os.path.join(self.opendirectory, 'chi')
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        self.savedirectory = newdir
        return
    
    directory_group = \
        Group(Item('opendirectory', label='Input dir.'),
              Item('savedirectory', label='Output dir.'),
              show_border=True,
              label='Files',
              )
    mask_group = \
        Group(Item('fit2dmask', label='Fit2D mask'),
              Item('addmask', label='Masks'),
              show_border=True,
              label='Masks',
              )
    
    geometry_group = \
        Group(Item('integrationspace', label='Integration space'),
              Item('wavelength', visible_when='integrationspace == "qspace"', label='Wavelength'),
              Item('xbeamcenter', label='x beamcenter'),
              Item('ybeamcenter', label='y beamcenter'),
              Item('distance', label='Distance'),
              Item('rotationd', label='Rotation'),
              Item('tiltd', label='Tilt rotation'),
              Item('tthstepd', label='Integration step', visible_when='integrationspace == "twotheta"'),
              Item('qstep', label='Integration step', visible_when='integrationspace == "qspace"'),

              show_border=True,
              label='Geometry parameters'
              ),

    basic_group = \
        Group(directory_group,
              mask_group,
              geometry_group,
              # label = 'Basic'
              )

    advanced_group = \
        Group(
              Group(Item('uncertaintyenable', label='Uncertainty'),
                    Item('sacorrectionenable', label='solid angle corr.'),
                    Item('polcorrectionenable', label='polarization corr.'),
                    Item('polcorrectf', label='polarization factor'),

                    show_border=True,
                    label='Corrections'
                    ),
              Group(Item('fliphorizontal', label='Flip horizontally'),
                    Item('flipvertical', label='Flip vertically'),
                    Item('xdimension', label='x dimension'),
                    Item('ydimension', label='y dimension'),
                    Item('xpixelsize', label='x pixel size'),
                    Item('ypixelsize', label='x pixel size'),
                    Item('maskedges', editor=ArrayEditor(width=-50)),

                    show_border=True,
                    label='Detector parameters'
                    ),

              # label = 'Advanced'
              )

    basic_view = \
        View(basic_group,

             resizable=True,
             scrollable=True,
             # handler = handler,
             icon=ImageResource('icon.ico'),
             )
    advanced_view = \
        View(advanced_group,

             resizable=True,
             scrollable=True,
             # handler = handler,
             icon=ImageResource('icon.ico'),
             )
    
    inst0 = Str('Caution! The calibration takes long time and program may lose response')
    inst1 = Str('Please specify the wavelength and distance between sample and detector')
    inst2 = Str('Plasee specify the initial value of following parameters')
    calibrate_View = \
        View(
            Group(
                Item('inst0', style='readonly', show_label=False),
                Item('inst1', style='readonly', show_label=False),
                HGroup(
                    Item('wavelength', visible_when='integrationspace == "qspace"', label='Wavelength'),
                    Item('distance', label='Distance'),
                    ),
                Item('inst2', style='readonly', show_label=False),
                HGroup(
                    Item('xbeamcenter', label='x beamcenter'),
                    Item('ybeamcenter', label='y beamcenter'),
                    ),
                HGroup(
                    Item('rotationd', label='Rotation'),
                    Item('tiltd', label='Tilt rotation')
                    ),

                show_border=True,
                label='Calibration'
                ),
             
             width=600,
             height=200,
             resizable=True,
             buttons=[OKButton, CancelButton],
             handler=CalibrationHandler(),
             icon=ImageResource('icon.ico'),
             )

    srx_view = \
        View(
             Group(basic_group,
                   advanced_group,

                   show_labels=False,
                   show_border=True,
                   layout='tabbed',
                   # layout = 'split',
                   # orientation = 'horizontal',
                   springy=True,
                   dock='tab',
                   ),
             width=600,
             height=800,
             resizable=True,
             # handler = handler,
             icon=ImageResource('icon.ico'),
             )

SrXconfig.initConfigClass()

if __name__ == '__main__':
    a = SrXConfig()
    # a.updateConfig()
    a.configure_traits(view='srx_view')
