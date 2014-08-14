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
if ETSConfig.toolkit == '' :
    ETSConfig.toolkit = 'qt4'
elif ETSConfig.toolkit == 'wx':
    try:
        import wx
        if wx.versions() > 2.8:
            ETSConfig.toolkit = 'qt4'
    except:
        ETSConfig.toolkit = 'qt4'

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

_optdatalist.append(
    ['toolkit', {'sec':'Misc', 'config':'n', 'header':'n',
                 'l':'toolkit',
                 'h':'toolkit of PDFgetEgui program, could be wx or qt4',
                 'c':['wx', 'qt4'],
                 'd':'qt4', }],
                    )

for i in _optdatalist:
    if i[0] == 'polcorrectionenable':
        i[1] = {'sec':'Others', 'args':'n', 'config':'n', 'header':'n',
                's':'polarcorr',
                'h':'enable polarization correction',
                'n':'?',
                'co':False,
                'd':False, }

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

    maskfile = File()

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

    def _maskfile_changed(self):
        if os.path.exists(self.maskfile):
            self.addmask = [self.maskfile]
        else:
            self.addmask = []
        return

    def _opendirectory_changed(self):
        if os.path.exists(self.opendirectory):
            newdir = os.path.join(self.opendirectory, 'chi')
            if not os.path.exists(newdir):
                try:
                    os.mkdir(newdir)
                except:
                    newdir = self.opendirectory
            self.savedirectory = newdir
        else:
            self.opendirectory = os.curdir
            self.savedirectory = os.curdir
        return
    
    def _savedirectory_changed(self):
        if not os.path.exists(self.savedirectory):
            self.savedirectory = os.curdir
        return
    
    configmode = Enum(['TEM', 'normal'])
    
    xpixelsizetem = Property(depends_on='xpixelsize, distance, wavelength')
    def _get_xpixelsizetem(self):
        return self.xpixelsize / self.distance / self.wavelength
    def _set_xpixelsizetem(self, size):
        size = float(size)
        self.updateConfig(xpixelsize=size * self.wavelength * self.distance)
        return
    ypixelsizetem = Property(depends_on='ypixelsize, distance, wavelength')
    def _get_ypixelsizetem(self):
        return self.ypixelsize / self.distance / self.wavelength
    def _set_ypixelsizetem(self, size):
        size = float(size)
        self.updateConfig(ypixelsize=size * self.wavelength * self.distance)
        return

    directory_group = \
        Group(Item('opendirectory', label='Input dir.', help='directory of 2D images'),
              Item('savedirectory', label='Output dir.', help='directory of saved files'),
              show_border=True,
              label='Files',
              )
    mask_group = \
        Group(Item('maskfile', label='Mask file'),
              show_border=True,
              label='Masks',
              )
        
    geometry_visible = Bool(False)
    geometry_group = \
        Group(Item('integrationspace', label='Integration grid'),
              Item('wavelength', visible_when='integrationspace == "qspace"', label='Wavelength',),
              Item('xbeamcenter', label='X beamcenter'),
              Item('ybeamcenter', label='Y beamcenter'),
              Item('distance', label='Camera length', visible_when='configmode == "TEM"'),
              Item('distance', label='Distance', visible_when='configmode == "normal"'),
              Item('rotationd', label='Rotation'),
              Item('tiltd', label='Tilt rotation'),
              Item('tthstepd', label='Integration step', visible_when='integrationspace == "twotheta"'),
              Item('qstep', label='Integration step', visible_when='integrationspace == "qspace"'),

              show_border=True,
              # label='Geometry parameters',
              visible_when='geometry_visible',
              )
    
    correction_visible = Bool(False)
    correction_group = \
        Group(Item('uncertaintyenable', label='Uncertainty'),
              Item('sacorrectionenable', label='solid angle corr.'),
              # Item('polcorrectionenable', label='polarization corr.'),
              # Item('polcorrectf', label='polarization factor'),
              
              show_border=True,
              # label='Corrections'
              visible_when='correction_visible'
              )
    
    detector_visible = Bool(False)
    detector_group = \
        Group(Item('fliphorizontal', label='Flip horizontally'),
              Item('flipvertical', label='Flip vertically'),
              Item('xdimension', label='x dimension'),
              Item('ydimension', label='y dimension'),
              Item('xpixelsize', label='x pixel size (mm)', visible_when='configmode == "normal"'),
              Item('ypixelsize', label='x pixel size (mm)', visible_when='configmode == "normal"'),
              Item('xpixelsizetem', label='x pixel size (A^-1)', tooltip='x pixel size, in A^-1', visible_when='configmode == "TEM"'),
              Item('ypixelsizetem', label='y pixel size (A^-1)', tooltip='y pixel size, in A^-1', visible_when='configmode == "TEM"'),
              Item('cropedges', label='Crop edges', editor=ArrayEditor(width=-50)),

              show_border=True,
              # label='Detector parameters'
              visible_when='detector_visible'
              ),

    main_view = \
        View(
            Group(
                directory_group,
                mask_group,
                Group(
                Item('configmode'),
                Group(Item('geometry_visible', label='Geometry parameters'),
                      geometry_group,),
                Group(Item('correction_visible', label='corrections'),
                      correction_group,),
                Group(Item('detector_visible', label='Detector parameters'),
                      detector_group,),
                # label = 'Basic'
                show_border=True,
                ),
                ),

             resizable=True,
             scrollable=True,
             # handler = handler,
             icon=ImageResource('icon.png'),
             )
        

SrXconfig.initConfigClass()

if __name__ == '__main__':
    a = SrXconfig()
    # a.updateConfig()
    a.configure_traits(view='main_view')
