"""
Created on 12 Nov 2020

@author: SMHI
"""

from filehandler.models import FileInfo
import fnmatch
import os, math
from sharkdata import settings
from sharkdata_core import string_utils


class DataFileInfo(object):
    def __init__(self, directory_path, file_name):
        self.directory_path = directory_path
        self.file_name = file_name

        self._set_variables_from_filename()

        modification_timestamp = math.floor(os.path.getmtime(self.get_file_path()))
        self.modification_timestamp = int(modification_timestamp)

        self.file_info = FileInfo.create(
            self.directory_path,
            self.file_name,
            self.name,
            self.version,
            self.datatype,
            self.modification_timestamp,
        )

    def get_file_path(self):
        return os.path.join(self.directory_path, self.file_name)

    def _set_variables_from_filename(self):
        parts = self.file_name.split("version")
        name = parts[0].strip("_").strip()
        version = parts[1].strip("_").strip() if len(parts) > 1 else ""
        parts = self.file_name.split("_")
        datatype = parts[1].strip("_").strip() if len(parts) > 1 else ""

        self.name = name
        self.version = version
        self.datatype = datatype

    def delete(self):
        self.to_file_info().delete()

    def save(self):
        self.to_file_info().save()

    def to_file_info(self):
        return self.file_info

    def __str__(self):
        return self.get_file_path()

    def __eq__(self, other):
        if other == None:
            return False
        elif type(other) == FileInfo:
            return self.to_file_info() == other
        return self.to_file_info() == other.to_file_info()

    def __hash__(self):
        return hash(self.to_file_info())


class ExportFileInfo(DataFileInfo):
    def _set_variables_from_filename(self):
        pattern_values = string_utils.extract_pattern_values(
            self.file_name,
            settings.EXPORTFORMATS_FILENAME_PATTERN,
            settings.FILENAME_PATTERN_VAR_START_SIGN,
            settings.FILENAME_PATTERN_VAR_STOP_SIGN,
        )

        self.format = pattern_values[settings.FILENAME_PATTERN_ID_FORMAT]
        self.datatype = pattern_values[settings.FILENAME_PATTERN_ID_DATATYPE]
        if settings.FILENAME_PATTERN_ID_YEAR in pattern_values:
            self.year = pattern_values[settings.FILENAME_PATTERN_ID_YEAR]
        else:
            self.year = ""

        self.approved = False  # TODO
        self.name = os.path.splitext(self.file_name)[0]

        self.log_file = (
            os.path.splitext(self.file_name)[0]
            + settings.EXPORTFORMATS_LOG_FILENAME_ENDING
        )
        self.log_file_path = os.path.join(self.directory_path, self.log_file)
        if not os.path.exists(self.log_file_path):
            self.log_file = ""
            self.log_file_path = ""

        self.generated_by = pattern_values[settings.FILENAME_PATTERN_ID_INSTITUTE]
        self.version = pattern_values[settings.FILENAME_PATTERN_ID_GENERATED]


class MonitoredDirectory(object):
    def __init__(self, directory_path, file_patterns=None, file_class=None):
        self.directory_path = directory_path
        if not type(file_patterns) is list:
            file_patterns = [file_patterns]
        self.file_patterns = file_patterns

        if file_class == None:
            file_class = DataFileInfo
        self.file_class = file_class

        self.new_files = []
        self.deleted_files = []
        self.modified_files = []

        self.refresh()

    def refresh(self):
        files_in_dir = [
            file
            for file_pattern in self.file_patterns
            for file in self.directory_path.glob(file_pattern)
        ]

        file_infos_in_dir = [
            self.file_class(self.directory_path, file.name)
            for file in files_in_dir
            if os.path.isfile(file)
        ]
        file_infos_in_dir = self._filter_latest_version_file_infos(file_infos_in_dir)

        file_infos_in_db = FileInfo.objects.all().filter(
            directory_path=self.directory_path
        )

        file_infos_in_db = [
            file_info
            for file_pattern in self.file_patterns
            for file_info in file_infos_in_db
            if fnmatch.fnmatch(file_info.file_name, file_pattern)
        ]

        filenames_in_db = [file_info.name for file_info in file_infos_in_db]
        filenames_in_dir = [file_info.name for file_info in file_infos_in_dir]

        self.new_files = [
            file_info
            for file_info in file_infos_in_dir
            if file_info.name not in filenames_in_db
        ]
        self.deleted_files = [
            file_info
            for file_info in file_infos_in_db
            if file_info.name not in filenames_in_dir
        ]
        self.modified_files = [
            file_info
            for file_info in file_infos_in_dir
            if (file_info not in self.new_files) and (file_info not in file_infos_in_db)
        ]

        for file_info in file_infos_in_db:
            file_info.delete()

        for file_info in file_infos_in_dir:
            file_info.save()

    def _filter_latest_version_file_infos(self, file_infos):
        file_versions = {}
        for file_info in file_infos:
            if file_info.name not in file_versions:
                file_versions[file_info.name] = []
            file_versions[file_info.name].append(file_info)

        filtered_file_infos = []
        for file_infos in file_versions.values():
            latest_file_info = None
            for file_info in file_infos:
                if (
                    latest_file_info == None
                    or file_info.version > latest_file_info.version
                ):
                    latest_file_info = file_info
            filtered_file_infos.append(latest_file_info)

        return filtered_file_infos

    def get_new_files(self):
        return self.new_files

    def get_deleted_files(self):
        return self.deleted_files

    def get_modified_files(self):
        return self.modified_files
