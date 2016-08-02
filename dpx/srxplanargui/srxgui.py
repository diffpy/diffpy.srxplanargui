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

from traits.etsconfig.api import ETSConfig
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
from pyface.api import ImageResource, SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.database import DatabaseSearcher, publish
from dpx.srxplanargui.srxconfig import SrXconfig
from diffpy.srxplanar.srxplanar import SrXplanar
from dpx.srxplanargui.help import SrXguiHelp
from dpx.srxplanargui.calibration import Calibration

from traits.api import push_exception_handler
push_exception_handler(reraise_exceptions=True)

class SrXguiHandler(Handler):

    def closed(self, info, is_ok):
        '''
        notify main gui to delete current plot in plots list
        '''
        configfile = info.object.detectConfigfile('default')
        info.object.saveConfig(configfile)
        return True

    def _saveconfigView(self, info):
        info.object._saveconfigView()
        return

    def _loadconfigView(self, info):
        info.object._loadconfigView()
        return

    def _helpView(self, info):
        info.object._helpbb_changed()
        return

class SaveHandler(Handler):

    def closed(self, info, is_ok):
        if is_ok:
            info.object.saveConfig(info.object.configfile)
        return True

class LoadHandler(Handler):
    def closed(self, info, is_ok):
        if is_ok:
            info.object.loadConfig(info.object.configfile)
        return

class SrXgui(HasTraits):

    addfiles = Instance(AddFiles)
    databasesearcher = Instance(DatabaseSearcher)
    srxconfig = Instance(SrXconfig)
    help = Instance(SrXguiHelp)
    splash = Any
    calibration = Instance(Calibration)

    def __init__(self, configfile=None, args=None, **kwargs):
        '''
        init the object, createt the notifications
        '''
        super(SrXgui, self).__init__(**kwargs)
        configfile = self.detectConfigfile(configfile)
        if not os.path.exists(configfile):
            configfile = self.detectConfigfile('default')
        self.configfile = configfile

        if not kwargs.has_key('srxconfig'):
            self.srxconfig = SrXconfig(filename=configfile, args=args, **kwargs)

        self.databasesearcher = DatabaseSearcher()
        self.srxconfig.databasesearcher = self.databasesearcher
        self.addfiles = AddFiles(srxconfig=self.srxconfig) 
        self.srx = SrXplanar(self.srxconfig)
        self.addfiles.srx = self.srx
        self.help = SrXguiHelp()
        self.calibration = Calibration(srx=self.srx, srxconfig=self.srxconfig)

        # self.loadConfig(configfile)
        self.splash.close()
        return

    def saveConfig(self, filename=None):
        '''
        save config
        '''
        if filename == 'default':
            filename = self.detectConfigfile(filename)
        self.srxconfig.writeConfig(filename, mode='full')
        self.configfile = filename
        return

    def loadConfig(self, filename=None):
        '''
        load config
        '''
        configfile = self.detectConfigfile(filename)
        if os.path.exists(configfile):
            self.srxconfig.updateConfig(filename=configfile)
            self.configfile = configfile
        return

    def processSelected(self, summation=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            if len(filelist) == 1:
                try:
                    header = self.addfiles.selected[0].header
                except: 
                    header = self.srxconfig.getHeader(mode='short')
            else:
                header = self.srxconfig.getHeader(mode='short')
            self.srx.prepareCalculation(filelist)
            if self.srxconfig.directory_visible:
                rv = self.srx.integrateFilelist(filelist, summation=summation)
            else:
                rv = self.srx.integrateFilelist(filelist, summation=summation, savefile=False)

            if self.srxconfig.database_visible:
                for r in rv:
                    publish(r['chi'], self.srxconfig.savedb, header)
        return

    def integrateFilelist(self, filelist, summation=None, filename=None, savefile=True, flip=None, correction=None, extramask=None):
        '''
        process all file in filelist, integrate them separately or together
        
        :param filelist: list of string, files to be integrated (full path)
        :param summation: bool or None, sum all files together or not, if None,
            use self.config.summation
        :param filename: file name of output file
        :param savefile: boolean, if True, save file to disk, if False, do not save file to disk
        :param flip: flip the image/2d array,
            if None: flip on the string/list of string, not flip on the 2d array
            Flip behavior is controlled in self.config
        :param correction: apply correction to the returned 2d array
            if None: correct on the string/list of string, not correct on the 2d array
        :param extramask: 2d array, extra mask applied in integration 
        
        :return: list of dict, in each dict, rv['chi'] is a 2d array of integrated intensity, shape is (2, len of intensity) 
            or (3, len of intensity) as [tth or q, intensity, (uncertainty)]. rv['filename'] is the 
            name of file to save to disk
        '''
        summation = self.config.summation if summation == None else summation

        if (summation)and(len(filelist) > 1):
            image = self._getPic(filelist, flip, correction)
            if filename == None:
                if isinstance(filelist[-1], str):
                    filename = os.path.splitext(filelist[-1])[0] + '_sum.chi'
                else:
                    filename = 'Sum_xrd.chi'
            rv = [self.integrate(image, savename=filename, savefile=savefile, extramask=extramask)]

        else:
            i = 0
            rv = []
            for imagefile in filelist:
                if filename == None:
                    rvv = self.integrate(imagefile, savefile=savefile, flip=flip, correction=correction, extramask=extramask)
                else:
                    rvv = self.integrate(imagefile, savename=filename + '%03d' % i, savefile=savefile,
                                         flip=flip, correction=correction, extramask=extramask)
                rv.append(rvv)

        return rv

    def detectConfigfile(self, filename):
        '''
        current directory > home directory, if none, then return the curdir+filename
        if 'default', then return home+filename
        '''
        if filename == None:
            configfile = os.path.join(os.path.curdir, 'srxconfig.cfg')
        elif filename == 'default':
            configfile = os.path.join(os.path.expanduser('~'), 'srxconfig.cfg')
        else:
            if os.path.abspath(filename):
                if os.path.exists(filename):
                    configfile = filename
                else:
                    filename = os.path.split(filename)[1]
                    configfile = os.path.join(os.path.curdir, filename)
            else:
                configfile = os.path.join(os.path.curdir, filename)
        return configfile


    ###########################################################
    def _saveconfigView(self):
        self.edit_traits(view='saveconfig_view')
        return
    def _loadconfigView(self):
        self.edit_traits(view='loadconfig_view')
        return

    configfile = File()
    helpbutton_action = \
        Action(name='Help ',
               action='_helpView')
    saveconfig_action = \
        Action(name='Save Config',
               action='_saveconfigView')
    loadconfig_action = \
        Action(name='Load Config',
               action='_loadconfigView')

    saveconfig_view = \
            View(Item('configfile'),

                 resizable=True,
                 title='Save config',
                 width=500,
                 buttons=[OKButton, CancelButton],
                 handler=SaveHandler(),
                 icon=ImageResource('icon.png'),
                 )
    loadconfig_view = \
            View(Item('configfile'),

                 resizable=True,
                 title='Load config',
                 width=500,
                 buttons=[OKButton, CancelButton],
                 handler=LoadHandler(),
                 icon=ImageResource('icon.png'),
                 )
    #############################################################

    def _integratbb_changed(self):
        self.processSelected(False)
        return

    def _integratessbb_changed(self):
        self.processSelected(True)
        return

    def _helpbb_changed(self):
        self.help.edit_traits(view='quickstart_view')
        return

    def _selfcalibratebb_changed(self):
        image = None
        if self.addfiles.selected != None:
            if len(self.addfiles.selected) == 1:
                image = self.addfiles.selected[0].fullname

        if image != None:
            self.calibration.image = image
        self.calibration.edit_traits(view='main_View')
        return

    integratbb = Button('Integrate')
    integratessbb = Button('Sum and Integrate')
    selfcalibratebb = Button('Calibrate')
    helpbb = Button('Help')

    traits_view = \
        View(
            HGroup(
                Item('addfiles', editor=InstanceEditor(view='traits_view'),
                     style='custom', label='Files', width=0.4),
                VGroup(
                    Group(Item('srxconfig', editor=InstanceEditor(view='main_view'),
                               style='custom', label='Basic', show_label=False),
                          springy=True,
                          ),
                    HGroup(spring,
                           Item('selfcalibratebb'),
                           Item('integratbb'),
                           spring,
                           show_labels=False,
                           ),
                    ),

                   layout='split',
                   springy=True,
                   dock='tab',
                   show_labels=False
                   ),
             resizable=True,
             title='SrXgui',
             width=700,
             height=650,
             kind='live',
             buttons=[helpbutton_action, saveconfig_action, loadconfig_action, OKButton],
             icon=ImageResource('icon.png'),
             handler=SrXguiHandler(),
             )

if __name__ == '__main__':
    sys.exit()
