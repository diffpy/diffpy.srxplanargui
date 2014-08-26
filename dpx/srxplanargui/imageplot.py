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
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, File, Any, Str
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, jet, Plot
from chaco.tools.api import PanTool, ZoomTool
from chaco.tools.image_inspector_tool import ImageInspectorTool, \
     ImageInspectorOverlay


class ImagePlot(HasTraits):
    imagefile = File
    srx = Any
    plot = Instance(Component)
    
    def createPlot(self):
        # image = np.log(self.srx.loadimage.loadImage(self.imagefile))
        image = self.srx.loadimage.loadImage(self.imagefile)
        xbounds = (0, image.shape[1])
        ybounds = (0, image.shape[0])
    
        pd = ArrayPlotData()
        pd.set_data("imagedata", image)
    
        plot = Plot(pd)
        img_plot = plot.img_plot("imagedata",
                                 xbounds=xbounds,
                                 ybounds=ybounds,
                                 colormap=jet)[0]
    
        # Tweak some of the plot properties
        plot.title = os.path.split(self.imagefile)[1]
        plot.padding = 50
    
        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)
        imgtool = ImageInspectorTool(img_plot)
        img_plot.tools.append(imgtool)
        overlay = ImageInspectorOverlay(component=img_plot, image_inspector=imgtool,
                                        bgcolor="white", border_visible=True)
    
        img_plot.overlays.append(overlay)
        self.plot = plot
        return plot
    
    hinttext = Str('Zoom: <z>;  Reset: <Esc>; Pan: <drag/drop>; Toggle XY coordinates: <P>')
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=(600, 600)),
                             show_label=False),
                        orientation="vertical"),
                    resizable=True, title='2D image',
                    statusbar=['hinttext'],
                    )
