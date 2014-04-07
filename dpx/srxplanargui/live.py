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
import threading
import time

# imports
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
from pyface.api import ImageResource, GUI
from enthought.pyface.api import SplashScreen

from dpx.srxplanargui.selectfiles import AddFiles
from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanargui.srxgui import SrXgui, SrXguiHandler
from diffpy.srxplanar.srxplanar import SrXplanar
from dpx.srxplanargui.help import SrXguiHelp

from dpx.confutils.tools import checkFileVal

class LivingThread(threading.Thread):

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
        return


class SrXguiLive(SrXgui):

    getxgui = Any

    def __init__(self, configfile=None, args=None, **kwargs):
        '''
        init the object, createt the notifications
        '''
        self.splash = SplashScreen(image=ImageResource('01.png'))
        self.splash.open()

        super(SrXgui, self).__init__(configfile=None, args=None, **kwargs)
        if not kwargs.has_key('srxconfig'):
            self.srxconfig = SrXconfig(filename=configfile, args=args, **kwargs)

        self.addfiles = AddFiles(srxconfig=self.srxconfig)
        self.srx = SrXplanar(self.srxconfig)
        self.help = SrXguiHelp()
        self.liveplot = None
        self.last10data = []

        self.loadConfig('default')
        self.splash.close()
        return

    @on_trait_change('srxconfig.savedirectory')
    def _changedir(self):
        if self.srxconfig.savedirectory.endswith('chi'):
            newdir = self.srxconfig.savedirectory[:-3] + 'pdf'
        else:
            newdir = os.path.join(self.srxconfig.savedirectory, 'pdf')
        self.getxgui.getxconfig.inputdir = self.srxconfig.savedirectory
        self.getxgui.getxconfig.savedir = newdir
        return

    def processSelected(self, ss=False):
        if self.addfiles.selected:
            self.srx.updateConfig()
            filelist = [f.fullname for f in self.addfiles.selected]
            self.srx.prepareCalculation(filelist)
            if ss:
                rvlist = self.srx.integrateFilelist(filelist, summation=True)
            else:
                rvlist = self.srx.integrateFilelist(filelist, summation=False)
            newchifilelist = [rv['filename'] for rv in rvlist]
            GUI.invoke_later(self.addNewImagesToGetXgui, newchifilelist)
        return

    def _startlivebb_changed(self):
        self.capturing = True

        wdir = self.srxconfig.opendirectory
        self.liveplot = None
        self.last10data = []
        self.srx.updateConfig()
        self.existfileset = self.srx.loadimage.genFileSet()

        self.livingthread = LivingThread(wdir, self)
        self.livingthread.daemon = True
        self.livingthread.start()
        return

    def _stoplivebb_changed(self):
        self.capturing = False
        self.livingthread.capturing = False
        self.livingthread.join()
        return

    ###LIVE###
    def newImages(self):
        newexistfileset = self.srx.loadimage.genFileSet()
        newfileset = newexistfileset - self.existfileset
        newfilelist = sorted(list(newfileset))
        newfilelistfull = map(lambda name: os.path.abspath(self.srxconfig.opendirectory + '/' + name), newfilelist)
        if len(newfilelist) > 0:
            for newfile in newfilelistfull:
                checkFileVal(newfile)
            if len(self.last10data) < 5:
                self.srx.prepareCalculation(newfilelistfull)
            rvlist = self.srx.integrateFilelist(newfilelistfull, summation=False)

            newchifilelist = [rv['filename'] for rv in rvlist]
            GUI.invoke_later(self.addNewImagesToGetXgui, newchifilelist)
            self.existfileset = newexistfileset
        return

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

    capturing = Bool(False)
    startlivebb = Button('Start capturing')
    stoplivebb = Button('Stop capturing')

    quickstart_action = \
        Action(name='Quick start',
               action='_quickstart')

    main_group = \
        HGroup(Item('addfiles', editor=InstanceEditor(view='traits_view'),
                    style='custom', label='Files', width=0.4),
               Group(Item('srxconfig', editor=InstanceEditor(view='basic_view'),
                          style='custom', label='Basic', show_label=False),
                     Item('srxconfig', editor=InstanceEditor(view='advanced_view'),
                          style='custom', label='Advanced', show_label=False),
                     layout='tabbed',
                     springy=True,
                     ),

               enabled_when='not capturing',
               layout='split',
               springy=True,
               dock='tab',
               show_labels=False
               )

    traits_view = \
        View(Group(main_group,
                   HGroup(spring,
                          Item('integratbb', enabled_when='not capturing',),
                          Item('integratessbb', enabled_when='not capturing',),
                          spring,
                          Item('startlivebb', enabled_when='capturing == False'),
                          Item('stoplivebb', enabled_when='capturing == True'),
                          spring,

                          show_labels=False,
                          ),
                   ),

             resizable=True,
             title='SrXgui',
             width=800,
             height=700,
             kind='live',
             icon=ImageResource('icon.ico'),
             handler=SrXguiHandler(),
             buttons=[OKButton, quickstart_action],
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
