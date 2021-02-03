#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.db import models


class Resources(models.Model):
    """Database table definition for resource files.
    Resources are stored in the FTP area.
    Resources are used for different kinds of needed data. for example
    species lists, header translations and different settings files.
    """

    #
    resource_name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=63)
    encoding = models.CharField(max_length=63)
    resource_file_name = models.CharField(max_length=255)
    ftp_file_path = models.CharField(max_length=1023)
    #
    file_content = models.TextField()  # BinaryField()
    #
    uploaded_by = models.CharField(max_length=255)
    uploaded_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.resource_name
