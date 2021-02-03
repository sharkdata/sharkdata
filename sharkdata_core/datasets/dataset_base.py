#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sharkdata_core

class DatasetBase(object):
    def __init__(self):
        """ Base class for datasets, mainly used for metadata. """
        super(DatasetBase, self).__init__()
        self._metadata = {}
        
    def clear(self):
        """ """
        self._metadata = {}

    def getMetadata(self, key):
        """ """
        return self._metadata.get(key, '')

    def addMetadata(self, key, value):
        """ """
        self._metadata[key] = value

#     def saveAsTextFile(self, file_name):
#         """ """
#         sharkdata_core.TextFiles().writeTableDataset(self, file_name)
#   
#     def saveAsExcelFile(self, file_name):
#         """ """
#         sharkdata_core.ExcelFiles().writeTableDataset(self, file_name)

