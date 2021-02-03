"""
Created on 12 Nov 2020

@author: SMHI
"""

from filehandler.models import FileInfo
import fnmatch
import os


class MonitoredDirectory(object):
    def __init__(self, directory_path, file_pattern=None):
        self.directory_path = directory_path
        self.file_pattern = file_pattern

        self.new_files = []
        self.deleted_files = []
        self.modified_files = []

        self.refresh()

    def refresh(self):
        files_in_dir = self.directory_path.glob(self.file_pattern)
        file_infos_in_dir = [
            FileInfo.create(self.directory_path, file.name)
            for file in files_in_dir
            if os.path.isfile(file)
        ]
        file_infos_in_dir = self._filter_latest_version_file_infos(file_infos_in_dir)

        file_infos_in_db = FileInfo.objects.all().filter(
            directory_path=self.directory_path
        )
        file_infos_in_db = [
            file_info
            for file_info in file_infos_in_db
            if fnmatch.fnmatch(file_info.file_name, self.file_pattern)
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
