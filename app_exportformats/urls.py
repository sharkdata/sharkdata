#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.urls import path
import app_exportformats.views

urlpatterns = [
    path("", app_exportformats.views.listExportFiles),
    path("list/", app_exportformats.views.listExportFiles),
    path("list.json/", app_exportformats.views.listExportFilesJson),
    #
    path("table/", app_exportformats.views.tableExportFilesText),
    path("table.txt/", app_exportformats.views.tableExportFilesText),
    path("table.json/", app_exportformats.views.tableExportFilesJson),
    
    path("<str:exportformat_name>/log.txt/", app_exportformats.views.downloadLogFile),
    path("<str:exportformat_name>/download", app_exportformats.views.downloadExportFile),
]
