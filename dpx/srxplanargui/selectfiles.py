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

import os
import sys
import fnmatch
import functools
import re

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt,\
    HasTraits, Property, Instance, Event, Button, Any, \
    on_trait_change, DelegatesTo, cached_property, property_depends_on

from traitsui.api import \
    Item, Group, View, Handler, spring, Action, \
    HGroup, VGroup, Tabbed, \
    RangeEditor, CheckListEditor, TextEditor, EnumEditor, ButtonEditor, \
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, OKCancelButtons
from traitsui.wx.table_editor import TableEditor as TableEditorWX

from traitsui.table_column import ObjectColumn
    
from collections import OrderedDict

from diffpy.pdfgetx.functs import sortKeyNumericString
from dpx.srxplanargui.datacontainer import DataContainer
from dpx.srxplanargui.srxconfig import SrXconfig

#-- The Live Search table editor definition ------------------------------------

class AddFilesHandler(Handler):
    
    def object_selectallbb_changed(self, info):
        '''
        select all files
        '''
        #FIXME
        try:
            editor = [aa for aa in info.ui._editors if isinstance(aa, TableEditorWX)][0]
            editor.selected_row_indices = editor.filtered_indices
            info.object.selected = [info.object.datafiles[i] for i in editor.filtered_indices]
            editor.refresh()
        except:
            pass
        return
    
class AddFiles(HasTraits):
    
    srxconfig = Instance(SrXconfig)
    
    # The currenty inputdir directory being searched:
    #inputdir = DelegatesTo('srxconfig')
    inputdir = Directory()#, entries = 10 )
    def _inputdir_default(self):
        return self.srxconfig.opendirectory
    # Should sub directories be included in the search:
    recursive = Bool(False)
    # The file types to include in the search:
    filetype = Enum('tif', 'all')
    # The current search string:
    search = Str
    # Is the search case sensitive?
    casesensitive = Bool(False)
    # The live search table filter:
    filter = Property # Instance( TableFilter )
    # The current list of source files being searched:
    datafiles = Property # List( string )
    # The currently selected source file:
    selected = Any # list( DtaContainer)
    dclick = Event
    # Summary of current number of files:
    summary = Property # Str
    # some meta data
    _filetypedict = {'tif': ['.tif', '.tiff', '.tif.bz2'],
                     'all': 'all',
                     }

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'search, casesensitive' )
    def _get_filter ( self ):
        '''
        get filename filter
        '''
        if len(self.search) == 0:
            return lambda x: True
        if self.casesensitive:
            rv = lambda x: fnmatch.fnmatchcase(x.basename, pat = '*'+self.search+'*')
        else:
            rv = lambda x: fnmatch.fnmatch(x.basename, pat = '*'+self.search+'*')
        return rv   
    
    refreshdatalist = Event
    @property_depends_on( 'inputdir, recursive, filetype, refreshdatalist' )
    def _get_datafiles ( self ):
        '''
        create a datacontainer list, all files under inputdir is filtered using filetype
        '''
        inputdir = self.inputdir
        if inputdir == '':
            inputdir = getcwd()

        filetypes = self._filetypedict[self.filetype]
        if self.recursive:
            rv = []
            for dirpath, dirnames, filenames in os.walk(inputdir):
                for filename in filenames:
                    if (os.path.splitext(filename)[1] in filetypes)or (filetypes=='all'):
                        rv.append(os.path.join(dirpath, filename))
        else:
            rv = [os.path.join(inputdir, filename)
                  for filename in os.listdir(inputdir)
                  if (os.path.splitext(filename)[1] in filetypes) or (filetypes=='all') ]
            
        rv.sort(key = sortKeyNumericString)
        rvlist = [DataContainer(fullname = fn) for fn in rv]
        return rvlist
        
    @property_depends_on('datafiles, search, casesensitive, selected')
    def _get_summary (self):
        '''
        get summary of file
        '''
        if self.selected and self.datafiles:
            rv = '%d files selected in a total of %d files.' % (len(self.selected), len(self.datafiles))
        else:
            rv = '0 files selected in a total of 0 files.'
        return rv
    
    @on_trait_change('srxconfig.opendirectory')
    def _changeInputdir(self):
        '''
        change inputdir of getxconfig
        '''
        self.inputdir = self.srxconfig.opendirectory
        return
    
    #-- Traits UI Views --------------------------------------------------------
    tableeditor = TableEditor(
        columns = [
            ObjectColumn(name = 'basename',
                         label = 'Name',
                         width = 0.70,
                         editable = False, 
                         ),
        ],
        auto_size = False,
        show_toolbar = False,
        show_lines = False, 
        #menu_name = 'rmenu',
        filter_name = 'filter',
        selection_mode = 'rows',
        selected = 'selected',
        dclick = 'dclick',
        )
    
    selectallbb = Button('Select all')
    
    traits_view = View(
        VGroup(
            VGroup(
                Group(
                    Item('filetype', label = 'Type' ),
                    Item('search',  id = 'search', width = 0.5,
                         editor = HistoryEditor(auto_set = False)),
                    ),
                Item('datafiles', id = 'datafiles', editor = tableeditor),
                Item('summary', editor = TitleEditor()),
                HGroup(spring,
                       Item('selectallbb', show_label=False),
                       spring,
                       ),
                dock = 'horizontal',
                show_labels = False
                ),
        ),
        #title     = 'Add files',
        #width     = 500,
        height    = 600,
        resizable = True,
        handler = AddFilesHandler(),
        )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    addfiles = AddFiles()
    addfiles.configure_traits() 
