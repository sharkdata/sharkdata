#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.urls import path
import app_ctdprofiles.views

urlpatterns = [
    path("", app_ctdprofiles.views.listCtdProfiles),
    path("list/", app_ctdprofiles.views.listCtdProfiles),
    path("list.json/", app_ctdprofiles.views.listCtdProfilesJson),
    #
    path("map/<str:profile_name>/", app_ctdprofiles.views.viewTestMap),
    path("plot/<str:profile_name>/", app_ctdprofiles.views.viewTestPlot),
    path("download/<str:profile_name>/", app_ctdprofiles.views.downloadTestPlot),
]
