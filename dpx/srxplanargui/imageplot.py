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

'''plot the 2d image
'''
import numpy as np
import os

# Enthought library imports
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

# Chaco imports
from enable.api import Component, ComponentEditor, BaseTool, KeySpec
from chaco.api import ArrayPlotData, jet, Plot
from chaco.tools.api import PanTool, ZoomTool, LineSegmentTool
from chaco.tools.image_inspector_tool import ImageInspectorTool, \
     ImageInspectorOverlay
from enable.colors import ColorTrait
from kiva.agg import points_in_polygon

class SaveLoadMaskHandler(Handler):

    def _save(self, info):
        '''
        save mask
        '''
        info.object.saveMaskFile()
        info.ui.dispose()
        return

    def _load(self, info):
        '''
        load mask
        '''
        info.object.loadMaskFile()
        info.ui.dispose()
        return

class AdvMaskHandler(Handler):

    def closed(self, info, is_ok):
        info.object.refreshImage()
        return

class ImagePlot(HasTraits):
    imagefile = File
    srx = Any
    srxconfig = Any
    plot = Instance(Component)
    maskfile = File
    pointmaskradius = Float(3.0)
    maskediting = Bool(False)

    brightpixel = Bool(True, desc='Mask the pixels too bright compared to their local environment')
    darkpixel = Bool(True, desc='Mask the pixels too dark compared to their local environment')
    avgmask = Bool(True, desc='Mask the pixels too bright or too dark compared to the average intensity at the similar diffraction angle')
    brightpixelr = Float(1.2, desc='Pixels with intensity large than this relative threshold (times the local environment) value will be masked')
    brightpixelsize = Int(5, desc='Size of testing area for detecting bright pixels')
    darkpixelr = Float(0.1, desc='Pixels with intensity less than this relative threshold (times the local environment) value will be masked')
    avgmaskhigh = Float(2.0, desc='Comparing to the average intensity at similar diffraction angle, \npixels with intensity larger than avg_int*high will be masked')
    avgmasklow = Float(0.5, desc='Comparing to the average intensity at similar diffraction angle, \npixels with intensity less than avg_int*low will be masked')
    cropedges = Array(dtype=np.int, desc='The number of pixels masked at each edge (left, right, top, bottom)')

    def createPlot(self):
        # image = np.log(self.srx.loadimage.loadImage(self.imagefile))
        image = self.srx.loadimage.loadImage(self.imagefile)
        self.maskfile = self.srxconfig.maskfile
        self.imageorg = image
        self.imageorglog = np.log(image)
        self.imageorglog[self.imageorglog < 0] = 0
        self.imageorgmax = image.max()
        self.imageorglogmax = self.imageorglog.max()
        self.mask = self.srx.mask.staticMask()

        if self.mask.shape != image.shape:
            self.maskfile = ''
            self.srxconfig.maskfile = ''
            self.srxconfig.ydimension = image.shape[0]
            self.srxconfig.xdimension = image.shape[1]
            self.mask = self.srx.mask.staticMask()

        y = np.arange(image.shape[0]).reshape((image.shape[0], 1)) * np.ones((1, image.shape[1]))
        x = np.arange(image.shape[1]).reshape((1, image.shape[1])) * np.ones((image.shape[0], 1))
        self.pts = np.array(np.vstack([x.ravel(), y.ravel()]).T)
        xbounds = (0, image.shape[1])
        ybounds = (0, image.shape[0])
        
        self.pd = ArrayPlotData()
        self.refreshImage(mask=self.mask, draw=False)
    
        self.plot = Plot(self.pd)
        self.img_plot = self.plot.img_plot("imagedata",
                                           xbounds=xbounds,
                                           ybounds=ybounds,
                                           colormap=jet,)[0]
        # Tweak some of the plot properties
        self.plot.title = os.path.split(self.imagefile)[1]
        self.plot.aspect_ratio = float(image.shape[1]) / float(image.shape[0])
        self.plot.padding = 50

        # Attach some tools to the plot
        self._appendTools()
        return

    def saveMaskFile(self):
        np.save(self.maskfile, self.mask)
        self.srxconfig.maskfile = self.maskfile
        return

    def loadMaskFile(self):
        if self.srxconfig.maskfile == self.maskfile:
            self.reloadMask()
        else:
            self.srxconfig.maskfile = self.maskfile
        return

    def mergeMask(self, points, remove=None):
        '''
        :param points: an Mx2 array of x,y point pairs (floating point) that define the
            boundaries of a polygon.
        :param remove: True for remove the new mask from the existing mask
        '''
        if remove == None:
            remove = self.removepolygonmask
        if len(points) > 2:
            mask = points_in_polygon(self.pts, points)
            mask = mask.reshape(self.mask.shape)
            if remove:
                self.mask = np.logical_and(self.mask, np.logical_not(mask))
            else:
                self.mask = np.logical_or(self.mask, mask)
            self.refreshImage()
        return

    def addPointMask(self, ndx, remove=None):
        '''
        :param ndx: (x,y) float
        '''
        x, y = ndx
        r = self.pts - np.array((x, y))
        r = np.sum(r ** 2, axis=1)
        mask = r < ((self.pointmaskradius + 1) ** 2)
        mask = mask.reshape(self.mask.shape)
        if remove:
            self.mask = np.logical_and(self.mask, np.logical_not(mask))
        else:
            self.mask = np.logical_or(self.mask, mask)
        self.refreshImage()
        return

    def clearMask(self):
        self.mask = self.mask * 0
        self.refreshImage()
        return

    maskaboveint = Int(10e10)
    maskbelowint = Int(1)

    def maskabove(self):
        mask = self.imageorg > self.maskaboveint
        self.mask = np.logical_or(self.mask, mask)
        self.refreshImage()
        return

    def maskbelow(self):
        mask = self.imageorg < self.maskbelowint
        self.mask = np.logical_or(self.mask, mask)
        self.refreshImage()
        return

    def genAdvMask(self):
        pic = self.imageorg
        if self.darkpixel or self.brightpixel:
            rv = np.zeros((self.srxconfig.ydimension, self.srxconfig.xdimension))
            if self.darkpixel:
                rv += self.srx.mask.darkPixelMask(pic)
            if self.brightpixel:
                rv += self.srx.mask.brightPixelMask(pic)
            dymask = np.logical_or((rv > 0), self.mask)
        else:
            dymask = self.mask
            
        if self.avgmask:
            cebak = self.srxconfig.cropedges
            self.srx.updateConfig(cropedges=self.cropedges)
            avgmask = self.srx.genAvgMask(pic, self.avgmaskhigh, self.avgmasklow, dymask)
            dymask = np.logical_or(dymask, avgmask)
            self.srx.updateConfig(cropedges=cebak)
        else:
            ones = np.ones((self.srxconfig.ydimension, self.srxconfig.xdimension), dtype=bool)
            ce = self.cropedges
            ones[ce[2]:-ce[3], ce[0]:-ce[1]] = dymask[ce[2]:-ce[3], ce[0]:-ce[1]]
            dymask = ones
        return dymask

    def previewAdvMask(self):
        dymask = self.genAdvMask()
        self.refreshImage(dymask)
        return

    def applyAdvMask(self):
        self._applyMaskPar()
        return

    def applyAdvMaskP(self):
        dymask = self.genAdvMask()
        self.mask = dymask
        self.refreshImage()
        self.brightpixel = False
        self.darkpixel = False
        self.avgmask = False
        self._applyMaskPar()
        return

    def _loadMaskPar(self):
        parlist = ['brightpixelmask', 'darkpixelmask', 'avgmask', 'brightpixelr',
                   'brightpixelsize', 'darkpixelr', 'avgmaskhigh', 'avgmasklow', 'cropedges']
        for p in parlist:
            setattr(self, p, getattr(self.srxconfig, p))
        return

    def _applyMaskPar(self):
        parlist = ['brightpixelmask', 'darkpixelmask', 'avgmask', 'brightpixelr',
                   'brightpixelsize', 'darkpixelr', 'avgmaskhigh', 'avgmasklow', 'cropedges']
        for p in parlist:
            setattr(self.srxconfig, p, getattr(self, p))
        return

    def _appendTools(self):
        '''
        append xy position, zoom, pan tools to plot

        :param plot: the plot object to append on
        '''
        plot = self.plot
        img_plot = self.img_plot

        # tools
        self.pan = PanTool(plot)
        self.zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        self.lstool = MasklineDrawer(self.plot, imageplot=self)
        self.xyseltool = MaskPointInspector(img_plot, imageplot=self)
        # self.lstool.imageplot = self

        img_plot.tools.append(self.xyseltool)
        overlay = ImageInspectorOverlay(component=img_plot, image_inspector=self.xyseltool,
                                        bgcolor="white", border_visible=True)
        img_plot.overlays.append(overlay)

        plot.tools.append(self.pan)
        plot.overlays.append(self.zoom)
        return

    def _enableMaskEditing(self):
        '''
        enable mask tool and disable pan tool
        '''
        self.maskediting = True
        for i in range(self.plot.tools.count(self.pan)):
            self.plot.tools.remove(self.pan)
        self.plot.overlays.append(self.lstool)
        self.titlebak = self.plot.title
        self.plot.title = 'Click: add a vertex; <Ctrl>+Click: remove a vertex; \n          <Enter>: finish the selection'
        return

    def _disableMaskEditing(self):
        '''
        disable mask tool and enable pan tool
        '''
        self.plot.overlays.remove(self.lstool)
        self.plot.tools.append(self.pan)
        self.plot.title = self.titlebak
        self.maskediting = False
        return

    def _enablePointMaskEditing(self):
        self.maskediting = True
        for i in range(self.plot.tools.count(self.pan)):
            self.plot.tools.remove(self.pan)
        self.titlebak = self.plot.title
        self.plot.title = 'Click: add a point; <Enter>: exit the point selection'
        return

    def _disablePointMaskEditing(self):
        self.plot.tools.append(self.pan)
        self.plot.title = self.titlebak
        self.maskediting = False
        return
    
    def refreshImage(self, mask=None, draw=True):
        '''
        recalculate the image using self.mask or mask and refresh display
        '''
        mask = self.mask if mask == None else mask
        image = self.applyScale()
        image = image * np.logical_not(mask) + mask * image.max()
        self.pd.set_data("imagedata", image)
        if draw:
            self.plot.invalidate_draw()
        return

    def reloadMask(self):
        '''
        reload the mask from file and refresh display
        '''
        self.mask = self.srx.mask.staticMask()
        self.refreshImage()
        return
    
    scalemode = Enum('linear', ['linear', 'log'], desc='Scale the image')
    scalepowder = Float(0.5, desc='gamma value to control the contrast')
    
    def applyScale(self, image=None):
        '''
        apply the scale to increase/decrease contrast
        '''
        if self.scalemode == 'linear':
            if image == None:
                image = self.imageorg
                intmax = self.imageorgmax
            else:
                image = image
                intmax = image.max()
        elif self.scalemode == 'log':
            if image == None:
                image = self.imageorglog
                intmax = self.imageorglogmax
            else:
                image = np.log(image)
                image[image < 0] = 0
                intmax = image.max()
        else:
            image = image
            intmax = image.max()
            
        image = intmax * ((image / intmax) ** self.scalepowder)
        return image
    
    splb = Float(0.0)
    spub = Float(1.0) 
    def _scalemode_changed(self):
        if self.scalemode == 'linear':
            self.scalepowder = 0.5
            self.splb = 0.0
            self.spub = 1.0
        elif self.scalemode == 'log':
            self.scalepowder = 1.0
            self.splb = 0.0
            self.spub = 4.0
        self.refreshImage()
        return
    
    def _scalepowder_changed(self, old, new):
        if np.round(old, 1) != np.round(new, 1):
            self.refreshImage()
        return

    def _add_notifications(self):
        self.on_trait_change(self.reloadMask, 'srxconfig.maskfile')
        return

    def _del_notifications(self):
        self.on_trait_change(self.reloadMask, 'srxconfig.maskfile', remove=True)
        return

    addpolygon_bb = Button('Add polygon mask')
    removepolygon_bb = Button('Remove polygon mask')
    addpoint_bb = Button('Add point mask')
    clearmask_bb = Button('Clear mask', desc='Clear the mask')
    advancedmask_bb = Button('Advanced mask', desc='The advanced mask is dynamically generated for each image.')
    maskabove_bb = Button('Mask intensity above')
    maskbelow_bb = Button('Mask intensity below')
    loadmaskfile_bb = Button('Load mask')
    savemaskfile_bb = Button('Save mask')

    def _addpolygon_bb_fired(self):
        self.removepolygonmask = False
        self._enableMaskEditing()
        return
    def _removepolygon_bb_fired(self):
        self.removepolygonmask = True
        self._enableMaskEditing()
        return
    def _addpoint_bb_fired(self):
        self._enablePointMaskEditing()
        self.xyseltool.enablemaskselect = True
        return
    def _clearmask_bb_fired(self):
        self.clearMask()
        return
    def _advancedmask_bb_fired(self):
        self.edit_traits('advancedmask_view')
        if not hasattr(self, 'advhint'):
            self.advhint = AdvHint()
            self.advhint.edit_traits('advhint_view')
        return
    def _maskabove_bb_fired(self):
        self.maskabove()
        return
    def _maskbelow_bb_fired(self):
        self.maskbelow()
        return
    def _loadmaskfile_bb_fired(self):
        self.edit_traits('loadmaskfile_view')
        return
    def _savemaskfile_bb_fired(self):
        self.maskfile = os.path.splitext(self.maskfile)[0] + '.npy'
        self.edit_traits('savemaskfile_view')
        return

    previewadvmask_bb = Button('Preview', desc='preview the dynamic mask for current image')
    applyadvmask_bb = Button('Apply', desc='apply the parameters and the dynamic mask will be generated during integration')
    applyadvmaskp_bb = Button('Apply permanently', desc='merge the current dynamic mask to the static mask')

    def _previewadvmask_bb_fired(self):
        self.previewAdvMask()
        return
    def _applyadvmask_bb_fired(self):
        self.applyAdvMask()
        return
    def _applyadvmaskp_bb_fired(self):
        self.applyAdvMaskP()
        return


    def __init__(self, **kwargs):
        '''
        init the object and create notification
        '''
        HasTraits.__init__(self, **kwargs)
        self.createPlot()
        self._loadMaskPar()
        self._add_notifications()
        return

    hinttext = Str('Zoom: <z>;  Reset: <Esc>; Pan: <drag/drop>; Toggle XY coordinates: <P>')
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=(550, 550)),
                             show_label=False),
                        HGroup(
                            spring,
                            Item('scalemode', label='Scale mode'),
                            Item('scalepowder', label='Gamma',
                                 editor=RangeEditor(auto_set=False, low_name='splb', high_name='spub', format='%.1f')),
                            spring,
                            ),
                        VGroup(
                            HGroup(
                                Item('addpolygon_bb', enabled_when='not maskediting'),
                                Item('removepolygon_bb', enabled_when='not maskediting'),
                                spring,
                                Item('maskabove_bb', enabled_when='not maskediting'),
                                Item('maskaboveint', enabled_when='not maskediting'),
                                show_labels=False,
                                ),
                            HGroup(
                                Item('addpoint_bb', enabled_when='not maskediting'),
                                Item('pointmaskradius', label='Size:', show_label=True),
                                spring,
                                Item('maskbelow_bb', enabled_when='not maskediting'),
                                Item('maskbelowint', enabled_when='not maskediting'),
                                show_labels=False,
                                ),
                            HGroup(
                                Item('clearmask_bb', enabled_when='not maskediting'),
                                Item('advancedmask_bb', enabled_when='not maskediting'),
                                spring,
                                Item('loadmaskfile_bb'),
                                Item('savemaskfile_bb'),
                                show_labels=False,
                                ),
                            show_labels=False,
                            show_border=True,
                            label='Mask'
                            ),
                        orientation="vertical"),
                    resizable=True,
                    title='2D image',
                    statusbar=['hinttext'],
                    width=600,
                    height=700,
                    icon=ImageResource('icon.png'),
                    )

    savemaskfile_action = \
        Action(name='OK ',
               action='_save')
    loadmaskfile_action = \
        Action(name='OK ',
               action='_load')

    savemaskfile_view = \
        View(Item('maskfile'),
             buttons=[savemaskfile_action, CancelButton],
             title='Save mask file',
             width=500,
             resizable=True,
             handler=SaveLoadMaskHandler(),
             icon=ImageResource('icon.png'),
             )

    loadmaskfile_view = \
        View(Item('maskfile'),
             buttons=[loadmaskfile_action, CancelButton],
             title='Load mask file',
             width=500,
             resizable=True,
             handler=SaveLoadMaskHandler(),
             icon=ImageResource('icon.png'),
             )


    advancedmask_view = \
        View(
            Group(
                VGroup(
                    Item('cropedges', label='Mask edges', editor=ArrayEditor(width=-50)),
                    label='Edge mask',
                    show_border=True,
                    ),
                VGroup(
                    Item('darkpixel', label='Enable'),
                    Item('darkpixelr', label='Threshold', enabled_when='darkpixel'),
                    label='Dark pixel mask',
                    show_border=True,
                    ),
                VGroup(
                    Item('brightpixel', label='Enable'),
                    Item('brightpixelsize', label='Testing size', enabled_when='brightpixel'),
                    Item('brightpixelr', label='Threshold', enabled_when='brightpixel'),
                    label='Bright pixel mask',
                    show_border=True,
                    ),
                VGroup(
                    Item('avgmask', label='Enable'),
                    Item('avgmaskhigh', label='High', enabled_when='avgmask'),
                    Item('avgmasklow', label='Low', enabled_when='avgmask'),
                    label='Average mask',
                    show_border=True,
                    ),
                HGroup(
                    spring,
                    Item('previewadvmask_bb'),
                    Item('applyadvmask_bb'),
                    Item('applyadvmaskp_bb'),
                    spring,

                    show_labels=False,
                    ),
                ),

             title='Advanced mask',
             width=320,
             handler=AdvMaskHandler(),
             resizable=True,
             buttons=[OKButton, CancelButton],
             icon=ImageResource('icon.png'),
             )

class MasklineDrawer(LineSegmentTool):
    """
    """

    imageplot = Any

    def _finalize_selection(self):
        self.imageplot._disableMaskEditing()
        self.imageplot.mergeMask(self.points)
        return

    def __init__(self, *args, **kwargs):
        LineSegmentTool.__init__(self, *args, **kwargs)
        self.line.line_color = "red"
        self.line.vertex_color = "white"
        return

class MaskPointInspector(ImageInspectorTool):

    exitmask_key = KeySpec('Enter')
    imageplot = Any
    enablemaskselect = Bool(False)

    def normal_key_pressed(self, event):
        if self.inspector_key.match(event):
            self.visible = not self.visible
            event.handled = True
        if self.exitmask_key.match(event):
            self.enablemaskselect = False
            self.imageplot._disablePointMaskEditing()
        return

    def normal_left_down(self, event):
        if self.enablemaskselect:
            ndx = self.component.map_index((event.x, event.y))
            self.imageplot.addPointMask(ndx)
        return

class AdvHint(HasTraits):

    advhinttext = str(
'''Notes: Advanced Masks are generated during the integration and refreshed for each image.
You can preview the masks here or apply the current masks to the static mask permanently.

Edge mask: mask the pixels around the image edge. (left, right, top, bottom)
Dark pixel mask: mask the pixels too dark compared to their local environment
Bright pixel mask: mask the pixels too bright compared to their local environment
Average mask: Mask the pixels too bright or too dark compared to the average intensity
    at the similar diffraction angle. Currect calibration information is required.''')

    advhint_view = \
        View(
            Group(
                Item('advhinttext', style='readonly', show_label=False),
                show_border=True,
                ),

             title='Advanced mask hints',
             width=640,
             resizable=False,
             buttons=[OKButton],
             icon=ImageResource('icon.png'),
             )
