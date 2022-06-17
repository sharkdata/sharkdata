#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.shortcuts import render
import app_datasets.models as datasets_models
import app_exportformats.models as exportformats_models


def viewDocumentation(request):
    
    return render(
        request,
        "documentation.html",
        {
            "first_dataset_name": _get_first_dataset_name(),
            "first_exportformat_name": _get_first_export_name(),
        },
    )

def _get_first_dataset_name():
    first_dataset_name = "SHARK_Example_dataset"
    if datasets_models.Datasets.objects.count() > 0:
        first_dataset = datasets_models.Datasets.objects.all().order_by("dataset_name")[
            0
        ]
        if first_dataset:
            first_dataset_name = first_dataset.dataset_name
        
    return first_dataset_name

def _get_first_export_name():
    first_export_name = "SHARK_Example_exportformat"
    if exportformats_models.ExportFiles.objects.count() > 0:
        first_exportformat = exportformats_models.ExportFiles.objects.all().order_by("export_name")[
            0
        ]
        if first_exportformat:
            first_export_name = first_exportformat.export_name
        
    return first_export_name

def viewExampleCode(request):
    """ """
    return render(request, "examplecode.html")


def viewDataPolicy(request):
    """ """
    return render(request, "datapolicy.html")


def viewAbout(request):
    """ """
    number_of_datasets = datasets_models.Datasets.objects.count()
    #
    return render(request, "about.html", {"number_of_datasets": number_of_datasets})
