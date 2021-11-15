#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.db import models


class ExportFiles(models.Model):
    """Database table definition for export files."""

    #
    format = models.CharField(max_length=63, default="")
    datatype = models.CharField(max_length=63, default="")
    year = models.CharField(max_length=4, default="")
    approved = models.BooleanField(default=False)
    status = models.CharField(max_length=63, default="")
    export_name = models.CharField(max_length=255, db_index=True, default="")
    export_file_name = models.CharField(max_length=255, default="")
    export_file_path = models.CharField(max_length=1023, default="")
    error_log_file = models.CharField(max_length=255, default="")
    error_log_file_path = models.CharField(max_length=1023, default="")
    #
    generated_by = models.CharField(max_length=255, default="")
    generated_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.export_file_name
