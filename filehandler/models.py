# -*- coding: utf-8 -*-

from django.db import models
import os
import math


class FileInfo(models.Model):
    """ Database table definition for FileInfo. """

    directory_path = models.CharField(max_length=1023)
    file_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=63)
    datatype = models.CharField(max_length=63)
    modification_timestamp = models.IntegerField()

    @classmethod
    def create(cls, directory_path, file_name, name, version, datatype, modification_timestamp):
        file_info = cls(
            directory_path=str(directory_path),
            file_name=file_name,
            name=name,
            version=version,
            datatype=datatype,
        )
        modification_timestamp = math.floor(os.path.getmtime(file_info.get_file_path()))
        file_info.modification_timestamp = int(modification_timestamp)
        return file_info

    def get_file_path(self):
        return os.path.join(self.directory_path, self.file_name)

    def __str__(self):
        return self.get_file_path()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if not isinstance(other, FileInfo):
            return False

        return (
            self.directory_path == other.directory_path
            and self.file_name == other.file_name
            and self.name == other.name
            and self.version == other.version
            and self.datatype == other.datatype
            and self.modification_timestamp == other.modification_timestamp
        )

    def __hash__(self):
        return hash(
            (
                self.directory_path,
                self.file_name,
                self.name,
                self.version,
                self.datatype,
                self.modification_timestamp,
            )
        )

