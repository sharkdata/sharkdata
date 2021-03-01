"""
Created on 11 Nov 2020

@author: SMHI
"""

from django.core.management.base import BaseCommand

from sharkdata_core import (
    SharkdataAdminUtils,
    DatasetUtils,
    ResourcesUtils,
    SharkArchiveFileReader,
)
import app_datasets.models as datasets_models
import app_ctdprofiles.models as ctdprofiles_models
import app_resources.models as resource_models
from filehandler.monitored_directory import MonitoredDirectory
import codecs
import pathlib
from enum import Enum
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

DATASET_FILE_PATTERN = "SHARK_*.zip"
PROFILE_FILENAME_STAR = "SHARK_Profile"

USER = "auto"


class DataType(Enum):
    DATASETS = "Datasets"
    RESOURCES = "Resources"


class Command(BaseCommand):
    help = "Synchronizes database based on available data in data folders"

    logfile_name = None

    def handle(self, *args, **options):
        logger.info("Synchronising data ...")
        self._init_log()
        try:
            error_counter = 0
            for data_type in DataType:
                error_counter += self._updateDb(data_type)

            if error_counter > 0:
                status = "FINISHED-" + str(error_counter) + "-errors"
            else:
                status = "FINISHED"

        except Exception as e:
            status = "FAILED"
            error_message = (
                "Failed when loading datasets or resources."
                + "\nException: "
                + str(e)
                + "\n"
            )
            self._write_log(error_message)
            logger.error("Data synchronisation failed! %s" % (error_message))

        finally:
            self._finalize_log(status)
            logger.info("Data synchronisation done.")

    def _init_log(self):
        self.logfile_name = SharkdataAdminUtils().log_create(
            command="Update datasets and resources", user="auto"
        )

    def _write_log(self, message):
        SharkdataAdminUtils().log_write(self.logfile_name, log_row=message)
        logger.debug(message)
        print(message)

    def _finalize_log(self, status):
        SharkdataAdminUtils().log_close(self.logfile_name, new_status=status)
        print("Log %s finalizes with status %s" % (self.logfile_name, status))

    def _updateDb(self, data_type):
        self._write_log("\n%s:" % (str(data_type.value)))

        error_counter = 0

        if data_type == DataType.DATASETS:
            monitored_dir = MonitoredDirectory(
                DatasetUtils()._data_in_datasets, DATASET_FILE_PATTERN
            )
            delete_func = self._deleteDatasetFromDb
            write_func = self._writeDatasetToDb
        elif data_type == DataType.RESOURCES:
            monitored_dir = MonitoredDirectory(ResourcesUtils()._data_in_resources, "*")
            delete_func = self._deleteResourceFromDb
            write_func = self._writeResourceToDb
        else:
            raise TypeError("Invalid data type %s!" % (str(data_type)))

        for deleted_file in monitored_dir.get_deleted_files():
            delete_func(deleted_file)
            self._write_log("Removing file: %s ..." % (deleted_file.file_name))

        for file_info in (
            monitored_dir.get_new_files() + monitored_dir.get_modified_files()
        ):
            try:
                self._write_log("Loading file: %s ..." % (file_info.file_name))
                write_func(file_info)
            except Exception as e:
                error_counter += 1
                self._write_log(
                    "ERROR: Failed to load: "
                    + file_info.file_name
                    + ". Error: "
                    + str(e)
                )

        return error_counter

    def _deleteResourceFromDb(self, file_info):
        try:
            db_resource = resource_models.Resources.objects.get(
                resource_file_name=file_info.file_name
            )
            db_resource.delete()
        except resource_models.Resources.DoesNotExist:
            pass  # Not found.

    def _writeResourceToDb(self, file_info):
        """ Extracts info from the resource file name and add to database. """

        # Extract info from file name.
        resource_name, resource_type, encoding = self.splitResourceFilename(
            file_info.file_name
        )
        #
        try:
            resource_file = codecs.open(
                file_info.get_file_path(), "r", encoding=encoding
            )
            resource_content = resource_file.read()
            resource_file.close()
        except:
            resource_content = "ERROR"

        self._deleteResourceFromDb(file_info)

        # Save to db.
        resources = resource_models.Resources(
            resource_name=resource_name,
            resource_type=resource_type,
            encoding=encoding,
            resource_file_name=file_info.file_name,
            ftp_file_path=file_info.get_file_path(),
            file_content=resource_content,
            uploaded_by=USER,
        )
        resources.save()

    def splitResourceFilename(self, file_name):
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

        return resource_name, resource_type, encoding

    def _deleteDatasetFromDb(self, file_info):
        try:
            db_dataset = datasets_models.Datasets.objects.get(
                dataset_name=file_info.name
            )
            db_dataset.delete()
        except datasets_models.Datasets.DoesNotExist:
            pass  # Not found.

    def _writeDatasetToDb(self, file_info):
        """ Extracts info from the dataset filename and from the zip file content and adds to database. """

        # Extract metadata parts.
        metadata = ""
        metadata_auto = ""

        with SharkArchiveFileReader(
            file_info.file_name, file_info.directory_path
        ) as zipreader:
            try:
                metadata = zipreader.getMetadataAsText()
                encoding = "cp1252"
                metadata = str(metadata, encoding, "strict")
            except Exception as e:
                self._write_log("WARNING: " + str(e))

            try:
                metadata_auto = zipreader.getMetadataAutoAsText()
                encoding = "cp1252"
                metadata_auto = str(metadata_auto, encoding, "strict")
            except Exception as e:
                self._write_log("WARNING: " + str(e))

            columndata_available = zipreader.isDataColumnsAvailable()

            # CTD profiles.
            ctd_profiles_table = None
            if file_info.file_name.startswith(PROFILE_FILENAME_STAR):
                ctd_profiles_table = zipreader.getDataAsText()

        self._deleteDatasetFromDb(file_info)

        # Save to db.
        dataset = datasets_models.Datasets(
            dataset_name=file_info.name,
            datatype=file_info.datatype,
            version=file_info.version,
            dataset_file_name=file_info.file_name,
            ftp_file_path=file_info.get_file_path(),
            content_data="NOT USED",
            content_metadata=metadata,
            content_metadata_auto=metadata_auto,
            column_data_available=columndata_available,
        )
        dataset.save()

        if ctd_profiles_table:
            # clear old data from DB
            ctdprofiles = ctdprofiles_models.CtdProfiles.objects.all().filter(
                dataset_file_name=file_info.file_name
            )
            for ctdprofile in ctdprofiles:
                ctdprofile.delete()

            data_header = []
            ctd_profiles_table = ctd_profiles_table.decode("cp1252")
            for index, row in enumerate(ctd_profiles_table.split("\n")):
                rowitems = row.strip().split("\t")
                if index == 0:
                    data_header = rowitems
                else:
                    if len(rowitems) > 1:
                        row_dict = dict(zip(data_header, rowitems))

                        water_depth_m = 0.0
                        try:
                            water_depth_m = float(row_dict.get("water_depth_m", -99))
                        except:
                            pass

                        db_profiles = ctdprofiles_models.CtdProfiles(
                            visit_year=row_dict.get("visit_year", ""),  # '2002',
                            platform_code=row_dict.get("platform_code", ""),  # 'Svea',
                            expedition_id=row_dict.get(
                                "expedition_id", ""
                            ),  # 'aa-bb-11',
                            visit_id=row_dict.get("visit_id", ""),  # '123456',
                            station_name=row_dict.get(
                                "station_name", ""
                            ),  # 'Station1A',
                            latitude=float(
                                row_dict.get("sample_latitude_dd", -99)
                            ),  # 70.00,
                            longitude=float(
                                row_dict.get("sample_longitude_dd", -99)
                            ),  # 10.00,
                            water_depth_m=water_depth_m,  # '80.0',
                            sampler_type_code=row_dict.get(
                                "sampler_type_code", ""
                            ),  # 'CTD',
                            sample_date=row_dict.get("visit_date", ""),  # '2000-01-01',
                            sample_project_code=row_dict.get(
                                "sample_project_code", ""
                            ),  # 'Proj',
                            sample_orderer_code=row_dict.get(
                                "sample_orderer_code", ""
                            ),  # 'Orderer',
                            sampling_laboratory_code=row_dict.get(
                                "sampling_laboratory_code", ""
                            ),  # 'Slabo',
                            revision_date=row_dict.get(
                                "revision_date", ""
                            ),  # '2010-10-10',
                            ctd_profile_name=row_dict.get(
                                "profile_file_name_db", ""
                            ),  # 'ctd.profile',
                            dataset_file_name=file_info.file_name,
                            ftp_file_path=file_info.get_file_path(),
                        )
                        db_profiles.save()
