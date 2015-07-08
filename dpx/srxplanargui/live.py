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
import re
import os
import sys
from functools import partial
import threading
import time

# break if help passed to the args
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
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor, InstanceEditor, ImageEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, MenuBar, OKCancelButtons
from pyface.api import ImageResource, GUI, SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanargui.srxgui import SrXgui, SrXguiHandler, SaveHandler, LoadHandler
from diffpy.srxplanar.srxplanar import SrXplanar
from dpx.srxplanargui.help import SrXguiHelp
from dpx.srxplanargui.calibration import Calibration

from dpx.confutils.tools import checkFileVal

'''class LivingThread(threading.Thread):

    def __init__(self, wdir, maingui):
        threading.Thread.__init__(self)
        self.daemon = True

        self.wdir = wdir
        self.maingui = maingui
        self.capturing = True
        self.lastmtime = os.path.getmtime(wdir)
        self.lastctime = os.path.getctime(wdir)
        self.lastatime = os.path.getatime(wdir)
        return

    def run(self):
        wdir = self.wdir
        maingui = self.maingui
        while self.capturing:
            if os.path.getatime(wdir) != self.lastatime:
                # GUI.invoke_later(maingui.newImages)
                maingui.newImages()
                self.lastatime = os.path.getatime(wdir)
            if os.path.getmtime(wdir) != self.lastmtime:
                # GUI.invoke_later(maingui.newImages)
                maingui.newImages()
                self.lastmtime = os.path.getmtime(wdir)
            if os.path.getctime(wdir) != self.lastctime:
                # GUI.invoke_later(maingui.newImages)
                maingui.newImages()
                self.lastctime = os.path.getctime(wdir)
            time.sleep(0.5)
        return'''


class SrXguiLive(SrXgui):

    getxgui = Any

    def __init__(self, configfile=None, args=None, **kwargs):
        
        # init the object, createt the notifications
        
        self.splash = SplashScreen(image=ImageResource('01.png'), show_log_messages=False)
        self.splash.open()

        super(SrXgui, self).__init__(**kwargs)
        configfile = self.detectConfigfile(configfile)
        if not os.path.exists(configfile):
            configfile = self.detectConfigfile('default')
        self.configfile = configfile

        if not kwargs.has_key('srxconfig'):
            self.srxconfig = SrXconfig(filename=configfile, args=args, **kwargs)

        self.addfiles = AddFiles(srxconfig=self.srxconfig)
        self.srx = SrXplanar(self.srxconfig)
        self.addfiles.srx = self.srx
        self.help = SrXguiHelp()
        self.calibration = Calibration(srx=self.srx, srxconfig=self.srxconfig)

        '''self.liveplot = None
        self.last10data = []'''

        self.splash.close()
        return

    @on_trait_change('srxconfig.savedirectory')
    def _changedir(self):
        newdir = self.srxconfig.savedirectory
        if os.path.exists(newdir):
            self.getxgui.getxconfig.inputdir = os.path.abspath(newdir)
            self.getxgui.getxconfig.savedir = os.path.abspath(newdir)
        else:
            self.getxgui.getxconfig.inputdir = os.path.abspath(os.path.curdir)
            self.getxgui.getxconfig.savedir = os.path.abspath(os.path.curdir)
        return

    def processSelected(self, summation=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            self.srx.prepareCalculation(filelist)
            rvlist = self.srx.integrateFilelist(filelist, summation=summation)
            newchifilelist = [rv['filename'] for rv in rvlist]
            GUI.invoke_later(self.addNewImagesToGetXgui, newchifilelist)
        return

    '''def _startCapturing(self):
        self.capturing = True

        wdir = self.srxconfig.opendirectory
        self.liveplot = None
        self.last10data = []
        self.srx.updateConfig()
        self.existfileset = self.srx.loadimage.genFileSet(fullpath=True)

        self.livingthread = LivingThread(wdir, self)
        self.livingthread.daemon = True
        self.livingthread.start()
        return'''

    '''def _stopCapturing(self):
        self.capturing = False
        self.livingthread.capturing = False
        self.livingthread.join()
        return'''

    '''###LIVE###
    def newImages(self):
        newexistfileset = self.srx.loadimage.genFileSet(fullpath=True)
        newfileset = newexistfileset - self.existfileset
        newfilelist = sorted(list(newfileset))
        if len(newfilelist) > 0:
            for newfile in newfilelist:
                checkFileVal(newfile)
            if len(self.last10data) < 5:
                self.srx.prepareCalculation(newfilelist)
            rvlist = self.srx.integrateFilelist(newfilelist, summation=False)

            newchifilelist = [rv['filename'] for rv in rvlist]
            GUI.invoke_later(self.addNewImagesToGetXgui, newchifilelist)
            self.existfileset = newexistfileset
        return'''

    def addNewImagesToGetXgui(self, filelist):
        '''
        add new images to getxgui, if images are already there, refresh them

        :param filelist: list of full path of new images
        '''
        self.addfiles.refreshdatalist = True

        newdatacontainers = self.getxgui.selectfiles.addFiles(filelist)
        self.last10data.extend(newdatacontainers)
        self.last10data = self.last10data[-10:]
        if (self.liveplot != None) and (self.liveplot in self.getxgui.plots):
            self.liveplot.datacontainers = self.last10data
        else:
            self.liveplot, liveplotpanel = self.getxgui.createNewPlot(newdatacontainers)
        return

    '''capturing = Bool(False)
    startcapturing_action = \
        Action(name='Start Capturing',
               action='_startCapturing',
               enabled_when='not capturing')
    stopcapturing_action = \
        Action(name='Stop Capturing',
               action='_stopCapturing',
               enabled_when='capturing')'''
    quickstart_action = \
        Action(name='Help ',
               action='_quickstart')
    saveconfig_action = \
        Action(name='Save Config',
               action='_saveconfigView',
               enabled_when='not capturing')
    loadconfig_action = \
        Action(name='Load Config',
               action='_loadconfigView',
               enabled_when='not capturing')

    traits_view = \
        View(
            HGroup(
                Item('addfiles', editor=InstanceEditor(view='traits_view'),
                     style='custom', label='Files', width=0.4),
                VGroup(
                    Group(Item('srxconfig', editor=InstanceEditor(view='main_view'),
                               style='custom', label='Basic', show_label=False),
                          # layout='tabbed',
                          springy=True,
                          ),
                    HGroup(spring,
                           Item('selfcalibratebb', enabled_when='not capturing'),
                           Item('integratbb', enabled_when='not capturing'),
                           # Item('integratessbb', enabled_when='not capturing'),
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
             icon=ImageResource('icon.png'),
             handler=SrXguiHandler(),
             # buttons=[quickstart_action, saveconfig_action, loadconfig_action,
             #         startcapturing_action, stopcapturing_action, OKButton],
             buttons=[quickstart_action, saveconfig_action, loadconfig_action, OKButton],
             )

def main():
    # splash = SplashScreen(image=ImageResource('splash.png'))
    # splash.open()

    # gui = SrXguiLive(splash=splash)
    gui = SrXguiLive()
    gui.configure_traits(view='traits_view')
    return

if __name__ == '__main__':
    sys.exit(main())
