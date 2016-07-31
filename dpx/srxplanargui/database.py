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

from pymongo import MongoClient
from databroker import DataBroker
from bson.objectid import ObjectId
from fractions import Fraction
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
from diffpy.pdfgetx.functs import loadData
from diffpy.pdfgetx.pdfgetter import PDFGetter

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
        info.object.selectfiles_obj.addDatalist(datafiles)
        info.ui.dispose()
        return

    def object_dclick_changed(self, info):
        info.object._plotbb_fired()
        return

class DatabaseSearcher(HasTraits):

    srxconfig = Instance(SrXconfig)
    pdfgetter = Instance(PDFGetter)
    selectfiles_obj = Any

    # The current list of documents being searched:
    datafiles = List(DataContainer)
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
    search = Button('Search')
    def _search_fired(self):
        d = self._daterange()
        e = self._experimenterlist()
        s = self._safN()
        c = self._comp()
        query = _merge_dicts(d, e, s, c)
        rv = DataBroker(**query)
        rv = [DataContainer(header=h) for h in rv]
        self.datafiles = rv
        return

    traits_view = View(
        Group(
            Group(
                HGroup(Item('composition'), 
                       Item('safN', label='SAF Number')),
                HGroup(Item('experimenters')),
                HGroup(Item('startdate', show_label=False), 
                       Item('enddate', label='< Experiment Date <')
                       ),
                HGroup(spring, Item('search'), show_labels=False),
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

# class DocumentContainer(DataContainer):
# 
#     getxconfig = Instance(GetXconfig)
#     pdfgetter = Instance(PDFGetter)
#     
#     formula = Any
#     datatype = Any
#     temperature = Any
#     mode = Any
#     deletable = Bool(True)
#     filepath = File
#     objectid = Property
# 
#     def write_to_disk(self, filepath=None):
#         if filepath:
#             self.filepath = filepath
#         self._write(self.filepath)
#         return
# 
#     def _connect(self):
#         database = self.fullname[:self.fullname.find('?')]
#         uri = up.parse_uri(database)
#         c = MongoClient(*uri['nodelist'][0], serverSelectionTimeoutMS=5000)
#         db = c[uri['database']]
#         return db[uri['collection']]
# 
#     def _write(self, filepath):
#         collection = self._connect()
# 
#         with open(filepath, 'w') as f:
#             try:
#                 doc = collection.find_one({'_id':ObjectId(self.objectid)}, 
#                                           {'file':1})
#             except Exception as e:
#                 print(e)
#                 return
#             for line in doc.get('file'):
#                 f.write(line)
# 
#         self._load()
#         return
# 
#     def _load(self):
#         if self.datatype == 'gr':
#             if os.path.exists(self.filepath):
#                 self._gr = loadData(self.filepath).transpose()
#                 self.lockdata = True
#         elif self.datatype == 'fq':
#             if os.path.exists(self.filepath):
#                 self._fq = loadData(self.filepath).transpose()
#                 self.lockdata = True
#         elif self.datatype == 'sq':
#             if os.path.exists(self.filepath):
#                 self._sq = loadData(self.filepath).transpose()
#                 self.lockdata = True
#         return
# 
#     def _save(self, typeofdata='gr', filename=None, filenameext=None):
#         '''
#         save data to disk
#         
#         :param filename: string, filename, only the base name of it will be used,
#             self.basename will be used if None
#         :param typeofdata: string, could be 'gr', 'iq', 'sq', 'fq'
#         :param filenameext: string, suffix of filename
#         '''
#         bbname = self.basename if filename == None else filename
#         if filenameext == None:
#             filenameext = ''
#         filename = os.path.splitext(bbname)[0] + filenameext + '.' + typeofdata
#         filepath = os.path.join(self.getxconfig.savedir, filename)
# 
#         # change the header information
#         self.getxconfig.inputfile = self.basename
#         self.getxconfig.outputtype = typeofdata
# 
#         if self.datatype == typeofdata:
#             if self.filepath == filepath:
#                 self.deletable = False
#             self._write(filepath)
#             return
# 
#         # export data
#         f = open(filepath, 'w')
#         f.write(self.getxconfig.getHeader(mode='short'))
#         f.write('#### start data\n')
#         f.write(getSL(typeofdata))
#         data = getattr(self, typeofdata).transpose()
#         np.savetxt(f, data, fmt='%g')
#         f.close()
#         return
# 
#     def _publish(self, typeofdata='gr', database=None):
#         if self.datatype == typeofdata:
#             collection = self._connect()
#             doc = collection.find_one({'_id': self.objectid})
#             publish_to_database(doc, database, self.temperature)
#             return
#         return super(DocumentContainer, self)._publish(typeofdata, database)
# 
#     def _getForm(self):
#         collection = self._connect()
#         return _get_formula(collection, self.objectid)
# 
#     def _getType(self):
#         collection = self._connect()
#         doc = collection.find_one({'_id': self.objectid}, {'datatype': 1})
#         return doc.get('datatype')
# 
#     def _getTemp(self):
#         collection = self._connect()
#         doc = collection.find_one({'_id': self.objectid}, {'temperature': 1})
#         return doc.get('temperature')
# 
#     def _getMode(self):
#         collection = self._connect()
#         doc = collection.find_one({'_id': self.objectid}, {'mode': 1})
#         return doc.get('mode')
# 
# 
#     @property_depends_on('fullname')
#     def _get_objectid(self):
#         return ObjectId(self.fullname[self.fullname.find('=')+1:])
# 
#     @property_depends_on('filepath')
#     def _get_basename(self):
#         return os.path.basename(self.filepath)
# 
#     @property_depends_on('filepath, refresh')
#     def _get_xrd(self):
#         '''
#         load the xrd data
#         '''
#         if os.path.exists(self.filepath) and (not self.lockdata):
#             rv = loadData(self.filepath).transpose()
#         else:
#             rv = np.arange(200).reshape(2, 100)
#         return rv
# 
#     def __init__(self, **kwargs):
#         HasTraits.__init__(self, **kwargs)
#         if self.formula == None:
#             self.formula = self._getForm()
#         if self.datatype == None:
#             self.datatype = self._getType()
#         if self.temperature == None:
#             self.temperature = self._getTemp()
#         if self.mode == None:
#             self.mode = self._getMode()
#         savedir = self.getxconfig.savedir if self.getxconfig.savedir else os.getcwd()
#         self.filepath = os.path.join(savedir, str(self.formula).replace('.', 'p'))
#         if self.temperature:
#             self.filepath += '_'
#             if self.temperature.is_integer():
#                 self.filepath += '%d' % self.temperature
#             else:
#                 self.filepath += str(self.temperature).replace('.', 'p')
#             self.filepath += 'K'
#         self.filepath += '.' + str(self.datatype)

def _merge_dicts(*dict_args):
    result = {}
    for d in dict_args:
        result.update(d)
    return result

def publish_to_database(doc, database, temperature=0):
    if doc.get('temperature') == None:
        doc['temperature'] = temperature
    uri = up.parse_uri('mongodb://' + database)
    c = MongoClient(*uri['nodelist'][0], serverSelectionTimeoutMS=5000)
    db = c[uri['database']]
    collection = db[uri['collection']]
    if collection.find(doc).limit(1).count(True) == 0:
        collection.insert_one(doc)
    return
