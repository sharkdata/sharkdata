# -*- coding: utf-8 -*-

from django.db import models


class CtdProfiles(models.Model):
    """ Database table definition for CTD profiles. """

    visit_year = models.CharField(max_length=63)
    platform_code = models.CharField(max_length=63)
    expedition_id = models.CharField(max_length=255)
    visit_id = models.CharField(max_length=255)
    station_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    water_depth_m = models.CharField(max_length=63)
    sampler_type_code = models.CharField(max_length=63)
    sample_date = models.CharField(max_length=63)
    sample_project_code = models.CharField(max_length=63)
    sample_orderer_code = models.CharField(max_length=63)
    sampling_laboratory_code = models.CharField(max_length=63)
    revision_date = models.CharField(max_length=63)
    ctd_profile_name = models.CharField(max_length=255)
    # Dataset.
    dataset_file_name = models.CharField(max_length=255)
    ftp_file_path = models.CharField(max_length=1023)

    def __str__(self):
        """ """
        return self.dataset_file_name
