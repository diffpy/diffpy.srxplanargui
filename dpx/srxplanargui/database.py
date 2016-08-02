#!/usr/bin/env python
##############################################################################
#
# dpx.pdfgetxgui    by Simon J. L. Billinge group
#                   (c) 2016 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Justin Calamari
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSENOTICE.txt for license information.
#
##############################################################################

import os
import sys
import re
import numpy as np

from pymongo import MongoClient, uri_parser as up
from databroker import DataBroker
from bson.objectid import ObjectId
from fractions import Fraction
from StringIO import StringIO
from datetime import datetime

from traits.api import \
    Dict, List, Enum, Bool, File, Float, Int, Array, Str, Range, Directory, CFloat, CInt, Color, \
    HasTraits, Property, Instance, Event, Button, Any, Date, \
    on_trait_change, DelegatesTo, cached_property, property_depends_on
    
from traitsui.api import \
    Item, Group, View, Handler, spring, Action, \
    HGroup, VGroup, Tabbed, \
    RangeEditor, CheckListEditor, TextEditor, EnumEditor, ButtonEditor, \
    ArrayEditor, TitleEditor, TableEditor, HistoryEditor
from traitsui.menu import ToolBar, OKButton, CancelButton, Menu, OKCancelButtons
from traitsui.table_column import ObjectColumn
from pyface.api import ImageResource

from dpx.srxplanargui.srxconfig import SrXconfig
from dpx.srxplanargui.datacontainer import DataContainer

from traits.api import push_exception_handler
push_exception_handler(reraise_exceptions=True)

class DatabaseSearcherHandler(Handler):

    def object_selectallbb_changed(self, info):
        '''
        select all files
        '''
        # FIXME
        try:
            editor = [
                aa for aa in info.ui._editors if isinstance(aa, TableEditorBE)][0]
            info.object.selected = [info.object.datafiles[i]
                                    for i in editor.filtered_indices]
            editor.refresh()
        except:
            pass
        return

    def _openFiles(self, info):
        '''
        add selected files to workspace and close panel
        '''
        datafiles = info.object.selected
        info.object.headers = [doc.header for doc in info.object.datafiles]
        info.ui.dispose()
        return

    def object_dclick_changed(self, info):
        datafiles = info.object.selected
        info.object.headers = [doc.header for doc in info.object.datafiles]
        return

class DatabaseSearcher(HasTraits):

    srxconfig = Instance(SrXconfig)

    # The current list of documents being searched:
    datafiles = List
    # The list of headers being opened
    headers = List
    # The currently selected documents:
    selected = Any
    dclick = Event
    # Summary of current number of documents:
    summary = Property
    # Database:
    startdate = Date
    enddate = Date
    composition = Str
    safN = Str
    experimenters = Str
    filter = Property

    def _daterange(self):
        range_ = {}
        if self.startdate:
            startdate = datetime.combine(self.startdate, datetime.min.time())
            range_['start_time'] = startdate
        if self.enddate:
            enddate = datetime.combine(self.enddate, datetime.min.time())
            range_['stop_time'] = enddate
        return range_

    def _comp(self):
        if self.composition:
            return {'sa_composition': self.composition}
        return {}

    def _safN(self):
        if self.safN:
            return {'bt_safN': self.safN}
        return {}

    def _experimenterlist(self):
        delimeters = ',\s*|;\s*|\s+'
        if self.experimenters:
            return {'bt_experimenters': 
                    {'$all': re.split(delimeters, self.experimenters)}}
        return {}

    def _get_filter(self):
        rv = lambda x: True
        return rv

    @property_depends_on('datafiles, selected')
    def _get_summary(self):
        '''
        get summary of file
        '''
        if self.selected and self.datafiles:
            rv = '%d files selected in a total of %d files.' % (len(self.selected), len(self.datafiles))
        else:
            rv = '0 files selected in a total of 0 files.'
        return rv

    #-- Traits UI Views --------------------------------------------------------
    tableeditor = TableEditor(
        columns=[
            ObjectColumn(name='composition',
                         width=1,
                         editable=False
                         ),
        ],
        auto_size=True,
        show_toolbar=False,
        show_lines=False,
        # menu_name = 'rmenu',
        filter_name='filter',
        selection_mode='rows',
        selected='selected',
        dclick='dclick',
        label_bg_color='(244, 243, 238)',
        cell_bg_color='(234, 233, 228)',
        )

    selectall_action = \
        Action(name='Select all',
               action='_selectall')
    open_action = \
        Action(name='Open',
               action='_openFiles')

    lastbb = Button('Last Run')
    def _lastbb_fired(self):
        self.datafiles = [DocumentContainer(header=DataBroker[-1])]
        return

    searchbb = Button('Search')
    def _searchbb_fired(self):
        d = self._daterange()
        e = self._experimenterlist()
        # s = self._safN()
        c = self._comp()
        query = _merge_dicts(d, e, c)
        rv = DataBroker(**query)
        rv = [DocumentContainer(header=h) for h in rv]
        self.datafiles = rv
        return

    traits_view = View(
        Group(
            Group(
                HGroup(Item('composition'), 
                       # Item('safN', label='SAF Number')
                       ),
                HGroup(Item('experimenters')),
                HGroup(Item('startdate', show_label=False), 
                       Item('enddate', label='< Experiment Date <')
                       ),
                HGroup(Item('lastbb'), spring, Item('searchbb'), show_labels=False),
                Item('datafiles', id='datafiles', editor=tableeditor, springy=True),
                Item('summary', editor=TitleEditor()),
                dock='horizontal',
                show_labels=False,
                ),
        ),
        title='Search the database',
        width=400,
        height=600,
        resizable=True,
        buttons=[selectall_action, open_action, CancelButton],
        icon=ImageResource('icon.png'),
        handler=DatabaseSearcherHandler,
        )

class DocumentContainer(DataContainer):

    header = Dict
    composition = Property

    @property_depends_on('header')
    def _get_composition(self):
        return self.header['start'].get('sa_composition')

    @property_depends_on('composition')
    def _get_basename(self):
        return self.composition + '.npy'

def _merge_dicts(*dict_args):
    result = {}
    for d in dict_args:
        result.update(d)
    return result

def _parse_header(header):
    rv = {}
    for line in header.splitlines():
        try:
            key, value = line.split(' = ')
            try:
                value = float(value)
            except ValueError:
                pass
            rv[key] = value if value else None
        except ValueError:
            pass
    return rv

def publish(chi, database, header):
    uri = up.parse_uri('mongodb://' + database)
    c = MongoClient(*uri['nodelist'][0], serverSelectionTimeoutMS=5000)
    db = c[uri['database']]
    collection = db[uri['collection']]
    if isinstance(header, basestring):
        header = _parse_header(header)
    image = StringIO()
    np.savetxt(image, chi.transpose(), fmt='%g')
    doc = _merge_dicts(header, {'file': image.getvalue()})
    if collection.find(doc).limit(1).count(True) == 0:
        collection.insert_one(doc)
    c.close()
    return
