#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.db import models


class Datasets(models.Model):
    """Database table definition for datasets.
    Datasets are stored in the FTP area. Datasets should follow
    the SHARK Archive Format both in file name and content.
    """

    #
    dataset_name = models.CharField(max_length=255)
    datatype = models.CharField(max_length=63)
    version = models.CharField(max_length=63)
    dataset_file_name = models.CharField(max_length=255)
    ftp_file_path = models.CharField(max_length=1023)
    #
    content_data = models.TextField()  # BinaryField()
    content_metadata = models.TextField()  # BinaryField()
    content_metadata_auto = models.TextField()  # BinaryField()
    #
    column_data_available = models.BooleanField(default=False)
    #
    uploaded_by = models.CharField(max_length=255)
    uploaded_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.dataset_name
