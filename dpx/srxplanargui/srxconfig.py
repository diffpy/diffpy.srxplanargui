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

from traits.api import Directory, String, List, Enum, Bool, File, Float, Int, \
                        HasTraits, Property, Range, cached_property, Str, Instance, Array,\
                        Event, CFloat, CInt, on_trait_change
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
    
    aa = Bool(True)
    
    def _preUpdateSelf(self, **kwargs):
        '''
        additional process called in self._updateSelf, this method is called
        before self._copySelftoConfig(), i.e. before copy options value to
        self.config (config file)
        
        check the tthmaxd and qmax, and set tthorqmax, tthorqstep according to integration space
        
        :param kwargs: optional kwargs
        '''
        self.tthmaxd, self.qmax = checkMax(self)
        if self.integrationspace == 'twotheta':
            self.tthorqmax = self.tthmax
            self.tthorqstep = self.tthstep
        elif self.integrationspace == 'qspace':
            self.tthorqmax = self.qmax
            self.tthorqstep = self.qstep
        return
    
    #def _postUpdateConfig(self, nofit2d=False, **kwargs):
    def _postUpdateConfig(self, **kwargs):
        '''
        post processing after parse args or kwargs, this method is called after 
        in self._postPocessing and before creating config file action  
        
        load fit2d config if specified in config, and set nocalculatio flag when create 
        config or create mask
        
        :param nofit2d: boolean, if True, it will skip loading fit2d calibration, this is useful
            when you reload/update some parameters but don't want to reload fit2d calibration 
            results.
        :param kwargs: optional kwargs
        '''
        '''if not nofit2d:
            self._loadFromFit2D(self.fit2dconfig)'''
        
        self._loadFromFit2D(self.fit2dconfig)
        if (self.createconfig!='')and(self.createconfig!=None):
            self.nocalculation = True
        if (self.createconfigfull!='')and(self.createconfigfull!=None):
            self.nocalculation = True
        if self.createmask!='':
            self.nocalculation = True
        return
    
    def _loadFromFit2D(self, filename):
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
    
    traits_view = View(Item('flipvertical', editor = BooleanEditor()),
                       Item('aa')
                       )

SrXConfig.initConfigClass()

if __name__=='__main__':
    a = SrXConfig()
    #a.updateConfig()
    a.configure_traits()
