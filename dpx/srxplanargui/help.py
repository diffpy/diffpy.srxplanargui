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
from traits.etsconfig.api import ETSConfig
from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt, \
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

    if sys.platform.startswith('win'):
        if ETSConfig.toolkit == 'qt4':
            hheight = 510
            hwidth = 960
        else:
            hheight = 556
            hwidth = 980
    else:
        hheight = 524
        hwidth = 964

    #######################
    # quick start
    #######################

    imgs = [ImageResource('%02d.png' % i) for i in range(1, 11)]

    qslen = Int(12)

    next_action = \
        Action(name='Next',
               action='_qsnext',
               enabled_when='object.qsindex<object.qslen'
               )
    previous_action = \
        Action(name='Previous',
               action='_qsprevious',
               enabled_when='object.qsindex>0'
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
        View(Item('qsimage', editor=ImageEditor(), width=0.5, show_label=False),
             title='Quick start',
             width=hwidth,
             height=hheight,
             resizable=True,
             buttons=[previous_action, next_action, OKButton],
             handler=HelpHandler(),
             icon=ImageResource('icon.png'),
             )
