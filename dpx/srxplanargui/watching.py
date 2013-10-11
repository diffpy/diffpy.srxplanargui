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

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanargui.srxgui import SrXgui

class Watching(HasTraits):
    
    srxconfig = Instance(SrXconfig)
    #SrXgui = Instance(SrXgui)
    
    
    
    
    
    