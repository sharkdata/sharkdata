#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import codecs
from django.conf import settings
import app_resources.models as models
from django.core.exceptions import ObjectDoesNotExist
import sharkdata_core


@sharkdata_core.singleton
class ResourcesUtils(object):
    """ Singleton class. """

    def __init__(self):
        """ """
        #         self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'resources')
        self._data_in_resources = settings.SHARKDATA_DATA_IN_RESOURCES
        self._data_resources = pathlib.Path(settings.SHARKDATA_DATA, "resources")

        self._resource_headers = None
        self._translated_headers = {}

    def clear(self):
        """ This must be called when new translate files are imported. """
        self._resource_headers = None
        self._translated_headers = {}

    def getResourceListHeaders(self):
        """ """
        if self._resource_headers == None:
            self._resource_headers = [
                "resource_name",
                "resource_type",
                "resource_file_name",
                "encoding",
            ]
        #
        return self._resource_headers

    def translateHeaders(
        self, data_header, resource_name="translate_headers", language="english"
    ):
        """ """
        if (resource_name, language) not in self._translated_headers:
            self._getTranslateHeaders(resource_name, language)
        #
        translated = []
        translate_dict = self._translated_headers[(resource_name.strip(), language)]
        for item in data_header:
            translated.append(
                translate_dict.get(item.strip(), item.strip())
            )  # Item value as default.
        #
        return translated

    def _getTranslateHeaders(
        self, resource_name="translate_headers", language="english"
    ):
        """ """
        translate_dict = {}
        columnindex = None

        resource = None
        try:
            resource = models.Resources.objects.get(resource_name=resource_name)
        except ObjectDoesNotExist:
            resource = None
        if resource:
            data_as_text = resource.file_content
            for index, row in enumerate(data_as_text.split("\n")):
                if index == 0:
                    columnindex = None
                    for index2, column in enumerate(row.split("\t")):
                        if language == column.strip():
                            columnindex = index2
                else:
                    if columnindex:
                        rowitems = row.split("\t")
                        if len(rowitems) > columnindex:
                            translate_dict[rowitems[0].strip()] = rowitems[
                                columnindex
                            ].strip()
        #
        self._translated_headers[(resource_name, language)] = translate_dict

    def writeResourcesInfoToDb(self, logfile_name, user=""):
        """Updates the database from datasets stored in the FTP area.
        I multiple versions of a dataset are in the FTP area only the latest
        will be loaded.
        """
        self.clear()
        error_counter = 0
        # Remove all db rows.
        models.Resources.objects.all().delete()
        # Get resources from FTP archive.
        for file_name in self.getResourceFiles():
            if logfile_name:
                sharkdata_core.SharkdataAdminUtils().log_write(
                    logfile_name, log_row="Loading file: " + file_name + "..."
                )
            try:
                error_string = self.writeFileInfoToDb(file_name, user)
                if error_string:
                    error_counter += 1
                    sharkdata_core.SharkdataAdminUtils().log_write(
                        logfile_name,
                        log_row="ERROR: Failed to load: "
                        + file_name
                        + ". Error: "
                        + error_string,
                    )
            except Exception as e:
                error_counter += 1
                sharkdata_core.SharkdataAdminUtils().log_write(
                    logfile_name,
                    log_row="ERROR: Failed to load: "
                    + file_name
                    + ". Error: "
                    + str(e),
                )
        #
        return error_counter

    def writeFileInfoToDb(self, file_name, user=""):
        """ Extracts info from the resource file name and add to database. """
        try:
            self.clear()
            #
            ftp_file_path = pathlib.Path(self._data_in_resources, file_name)
            # Extract info from file name.
            resource_name, resource_type, encoding = self.splitFilename(file_name)
            #
            try:
                resource_file = codecs.open(ftp_file_path, "r", encoding=encoding)
                resource_content = resource_file.read()
                resource_file.close()
            except:
                resource_content = "ERROR"

            # Save to db.
            resources = models.Resources(
                resource_name=resource_name,
                resource_type=resource_type,
                encoding=encoding,
                resource_file_name=file_name,
                ftp_file_path=ftp_file_path,
                file_content=resource_content,
                uploaded_by=user,
            )
            resources.save()
        except Exception as e:
            return str(e)

    def getResourceFiles(self):
        """ Read filenames from FTP area. """
        resource_files = []
        for file_name in self._data_in_resources.glob("*"):
            file_path = pathlib.Path(self._data_in_resources, file_name)
            if file_path.is_file():
                resource_files.append(str(file_name))
        #
        return resource_files

    def splitFilename(self, file_name):
        """ Extract parts from file name. """
        filename = pathlib.Path(file_name).stem
        resource_name = filename.strip("_").strip()
        parts = filename.split("_")
        resource_type = parts[0].strip("_").strip()
        #
        encoding = "windows-1252"
        if "utf8" in filename.lower():
            encoding = "utf-8"
            resource_name = (
                resource_name.replace("utf8", "").replace("__", "_").strip("_").strip()
            )
        if "utf-8" in filename.lower():
            encoding = "utf-8"
            resource_name = (
                resource_name.replace("utf-8", "").replace("__", "_").strip("_").strip()
            )
        #
        return resource_name, resource_type, encoding
