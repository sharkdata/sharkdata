#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.urls import path
import app_datasets.views

urlpatterns = [
    path("", app_datasets.views.listDatasets),
    path("list/", app_datasets.views.listDatasets),
    path("list.json/", app_datasets.views.listDatasetsJson),
    #
    path("table/", app_datasets.views.tableDatasetsText),
    path("table.txt/", app_datasets.views.tableDatasetsText),
    path("table.json/", app_datasets.views.tableDatasetsJson),
    #
    path("<str:dataset_name>/data.txt/", app_datasets.views.datasetDataText),
    path("<str:dataset_name>/data.json/", app_datasets.views.datasetDataJson),
    path(
        "<str:dataset_name>/data_columns.txt/",
        app_datasets.views.datasetDataColumnsText,
    ),
    path(
        "<vdataset_name>/data_columns.json/", app_datasets.views.datasetDataColumnsJson
    ),
    #
    path("<str:dataset_name>/metadata.txt/", app_datasets.views.datasetMetadataText),
    path("<str:dataset_name>/metadata.json/", app_datasets.views.datasetMetadataJson),
    path("<str:dataset_name>/shark_archive.zip/", app_datasets.views.sharkArchiveZip),
]
