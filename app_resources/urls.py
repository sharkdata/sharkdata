#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.urls import path
import app_resources.views

urlpatterns = [
    path("", app_resources.views.listResources),
    path("list/", app_resources.views.listResources),
    path("list.json/", app_resources.views.listResourcesJson),
    #
    path("table/", app_resources.views.tableResourcesText),
    path("table.txt/", app_resources.views.tableResourcesText),
    path("table.json/", app_resources.views.tableResourcesJson),
    #
    path("<str:resource_name>/content.txt/", app_resources.views.resourceContentText),
]
