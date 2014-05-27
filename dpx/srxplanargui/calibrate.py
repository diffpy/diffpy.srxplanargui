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

import numpy as np
import os
import sys
import re

from traits.etsconfig.api import ETSConfig
if ETSConfig.toolkit == 'wx':
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
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, ImageEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons

from dpx.srxplanargui.srxconfig import SrXconfig
# from diffpy.srxplanar.srxplanar import SrXplanar

class Calibration(HasTraits):
    image = File
    dspacefile = File
    srxconfig = Instance(SrXconfig)
    pythonbin = File
    caliscript = File
    
    xpixelsize = DelegatesTo('srxconfig')
    ypixelsize = DelegatesTo('srxconfig')
    wavelength = DelegatesTo('srxconfig')
    xbeamcenter = DelegatesTo('srxconfig')
    ybeamcenter = DelegatesTo('srxconfig')
    xdimension = DelegatesTo('srxconfig')
    ydimension = DelegatesTo('srxconfig')
    distance = DelegatesTo('srxconfig')
    rotationd = DelegatesTo('srxconfig')
    tiltd = DelegatesTo('srxconfig')
    
    def locatePyFAI(self):
        pythonbin = sys.executable
        
        if sys.platform == 'win32':
            caliscripts = os.path.join(sys.exec_prefix, 'Scripts', 'pyFAI-calib.py')
        elif sys.platform == 'linux2':
            caliscript = os.path.join(sys.exec_prefix, 'bin', 'pyFAI-calib')
        else:
            caliscript = os.path.join(sys.exec_prefix, 'bin', 'pyFAI-calib')
        
        self.pythonbin = pythonbin
        self.caliscript = caliscript
        return
        
    def callPyFAICalibration(self, image=None, dspacefile=None):
        if image == None:
            image = self.image
        else:
            self.image = image
        if dspacefile == None:
            dspacefile = self.dspacefile
        else:
            self.dspacefile = dspacefile
        
        image = os.path.abspath(image)
        dspacefile = os.path.abspath(dspacefile)
        
        ps = [self.xpixelsize * 1000, self.ypixelsize * 1000]
        
        calicmd = [self.pythonbin, self.caliscript]
        calicmd.extend(['-w', str(self.wavelength)])
        calicmd.extend(['-S', str(dspacefile)])
        calicmd.extend(['-p', str(ps[0]) + ',' + str(ps[1])])
        calicmd.extend([str(image)])
        
        import subprocess
        subprocess.call(calicmd)
        return
    
    def parsePyFAIoutput(self, image=None):
        if image == None:
            image = self.image
        
        filename = os.path.splitext(image)[0] + '.xy'
        if os.path.exists(filename):
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
        for line in lines:
            if re.search('# Distance Sample-beamCenter', line):
                distance = findFloat(line)[0]
            elif re.search('# Center', line):
                x, y = findFloat(line)
            elif re.search('# Tilt', line):
                tiltd, rotationd = findFloat(line)
        
        self.distance = distance
        self.xbeamcenter = x - 0.5
        self.ybeamcenter = self.ydimension - y - 0.5
        self.tiltd = tiltd
        self.rotationd = rotationd
        return
        
        
def findFloat(line):
    temp = re.findall('[-+]?\d*\.\d+|[-+]?\d+', line)
    return map(float, temp)
    
if __name__ == '__main__':
    srxconfig = SrXconfig()
    cali = Calibration(srxconfig=srxconfig)
    cali.locatePyFAI()
    cali.callPyFAICalibration('ceo2.tif', 'ceo2.d')
    cali.parsePyFAIoutput()
    cali.configure_traits()
    
