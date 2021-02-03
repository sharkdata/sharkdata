#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib

from django.conf import settings
import app_datasets.models as datasets_models
import app_ctdprofiles.models as ctdprofiles_models
import sharkdata_core


@sharkdata_core.singleton
class DatasetUtils(object):
    """ Singleton class. """

    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._data_in_datasets = settings.SHARKDATA_DATA_IN_DATASETS
        self._data_datasets = pathlib.Path(settings.SHARKDATA_DATA, "datasets")
        self._metadata_update_thread = None
        self._generate_archives_thread = None

    def translateDataHeaders(
        self, data_header, resource_name="translate_headers", language="darwin_core"
    ):
        #                        language = 'english'):
        """ """
        return sharkdata_core.ResourcesUtils().translateHeaders(
            data_header, resource_name, language
        )

    def getDatasetListHeaders(self):
        """ """
        if not self._data_header:
            self._data_header = [
                "dataset_name",
                "datatype",
                "version",
                "dataset_file_name",
            ]
        #
        return self._data_header

    def translateDatasetListHeaders(self, data_header, language=None):
        """ """
        #         if not language:
        #             return data_header
        #
        translated = []
        #
        if not self._translations:
            self._translations = {
                "dataset_name": "Dataset name",
                "datatype": "Datatype",
                "version": "Version",
                "dataset_file_name": "File name",
            }
        #
        for item in data_header:
            if item in self._translations:
                translated.append(self._translations[item])
            else:
                translated.append(item)
        #
        return translated

    def getDataAsText(self, dataset_name):
        """ Data is not stored in database, get from zip file."""
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        #
        # Extract data part.
        data_content = ""
        zipreader = sharkdata_core.SharkArchiveFileReader(
            db_dataset.dataset_file_name, self._data_in_datasets
        )
        try:
            zipreader.open()
            data_content = zipreader.getDataAsText().decode(
                "cp1252"
            )  # Default encoding in archive data.

        finally:
            zipreader.close()
        #             print(data_content)
        #
        return data_content

    def getDataColumnsAsText(self, dataset_name):
        """ Data is not stored in database, get from zip file."""
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        #
        # Extract data part.
        data_content = ""
        zipreader = sharkdata_core.SharkArchiveFileReader(
            db_dataset.dataset_file_name, self._data_in_datasets
        )
        try:
            zipreader.open()
            data_content = zipreader.getDataColumnsAsText().decode(
                "cp1252"
            )  # Default encoding in archive data.

        finally:
            zipreader.close()
        #             print(data_content)
        #
        return data_content

    def getMetadataAsText(self, dataset_name):
        """ """
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        # Fix line breaks for windows. Remove rows with no key-value-pairs.
        metadata_list = []
        concat_metadata = (
            db_dataset.content_metadata + "\n" + db_dataset.content_metadata_auto
        )
        for row in concat_metadata.split("\n"):
            if ":" in row:
                parts = row.split(":", 1)  # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_list.append(key + ": " + value)
        #
        return "\r\n".join(metadata_list)

    def writeLatestDatasetsInfoToDb(self, logfile_name=None, user=""):
        """Updates the database from datasets stored in the FTP area.
        I multiple versions of a dataset are in the FTP area only the latest
        will be loaded.
        """

        # Check dataset in 'data_in/datasets'. Create a list of dataset names.
        dataset_names = []
        for dataset_path in self._data_in_datasets.glob("SHARK_*.zip"):
            print(dataset_path.name)
            parts = dataset_path.name.split("_version")
            if len(parts) >= 1:
                dataset_names.append(parts[0])

        # Remove all datasets from 'data/datasets' not included in 'dataset_names'.
        for dataset_path in self._data_datasets.glob("SHARK_*.zip"):
            print(dataset_path.name)
            parts = dataset_path.name.split("_version")
            if len(parts) >= 1:
                if parts[0] not in dataset_names:
                    # Delete the file.
                    dataset_path.unlink()  # Removes file.
                    # Remove from database.
                    datasets_models.Datasets.objects.get(
                        dataset_name=dataset_path.name
                    ).delete()

        error_counter = 0
        # Remove all db rows.
        datasets_models.Datasets.objects.all().delete()

        # CTD profiles.
        ctdprofiles_models.CtdProfiles.objects.all().delete()

        # Get latest datasets from FTP archive.
        archive = sharkdata_core.SharkArchive(self._data_in_datasets)
        for file_name in sorted(archive.getLatestSharkArchiveFilenames()):
            if logfile_name:
                sharkdata_core.SharkdataAdminUtils().log_write(
                    logfile_name, log_row="Loading file: " + file_name + "..."
                )
            try:
                error_string = self.writeFileInfoToDb(file_name, logfile_name, user)
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

    def writeFileInfoToDb(self, file_name, logfile_name=None, user=""):
        """ Extracts info from the dataset filename and from the zip file content and adds to database. """
        try:
            #
            ftp_file_path = pathlib.Path(self._data_in_datasets, file_name)
            # Extract info from file name.
            dataset_name, datatype, version = self.splitFilename(file_name)
            # Extract metadata parts.
            metadata = ""
            metadata_auto = ""
            columndata_available = False
            #
            zipreader = sharkdata_core.SharkArchiveFileReader(
                file_name, self._data_in_datasets
            )
            try:
                zipreader.open()
                #
                try:
                    metadata = zipreader.getMetadataAsText()
                    encoding = "cp1252"
                    metadata = str(metadata, encoding, "strict")
                except Exception as e:
                    sharkdata_core.SharkdataAdminUtils().log_write(
                        logfile_name, log_row="WARNING: " + str(e)
                    )
                #
                try:
                    metadata_auto = zipreader.getMetadataAutoAsText()
                    encoding = "cp1252"
                    metadata_auto = str(metadata_auto, encoding, "strict")
                except Exception as e:
                    sharkdata_core.SharkdataAdminUtils().log_write(
                        logfile_name, log_row="WARNING: " + str(e)
                    )
                #
                columndata_available = zipreader.isDataColumnsAvailable()

                # CTD profiles.
                ctd_profiles_table = None

                # if datatype == 'CTDprofile':
                if datatype == "Profile":
                    ctd_profiles_table = zipreader.getDataAsText()

            finally:
                zipreader.close()

            # Remove from database.
            try:
                db_dataset = datasets_models.Datasets.objects.get(
                    dataset_name=dataset_name
                )
                db_dataset.delete()
            except datasets_models.Datasets.DoesNotExist:
                pass  # Not found.

            # Save to db.
            dataset = datasets_models.Datasets(
                dataset_name=dataset_name,
                datatype=datatype,
                version=version,
                dataset_file_name=file_name,
                ftp_file_path=ftp_file_path,
                content_data="NOT USED",
                content_metadata=metadata,
                content_metadata_auto=metadata_auto,
                #
                column_data_available=columndata_available,
            )
            dataset.save()

            if ctd_profiles_table:
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
                                water_depth_m = float(
                                    row_dict.get("water_depth_m", -99)
                                )
                            except:
                                pass

                            db_profiles = ctdprofiles_models.CtdProfiles(
                                visit_year=row_dict.get("visit_year", ""),  # '2002',
                                platform_code=row_dict.get(
                                    "platform_code", ""
                                ),  # 'Svea',
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
                                sample_date=row_dict.get(
                                    "visit_date", ""
                                ),  # '2000-01-01',
                                sample_project_code=row_dict.get(
                                    "sample_project_code", ""
                                ),  # 'Proj',
                                #                                 sample_project_code = row_dict.get('sample_project_name_sv', ''), # 'Proj',
                                sample_orderer_code=row_dict.get(
                                    "sample_orderer_code", ""
                                ),  # 'Orderer',
                                #                                 sample_orderer_code = row_dict.get('sample_orderer_name_sv', ''), # 'Orderer',
                                sampling_laboratory_code=row_dict.get(
                                    "sampling_laboratory_code", ""
                                ),  # 'Slabo',
                                #                                 sampling_laboratory_code = row_dict.get('sampling_laboratory_name_sv', ''), # 'Slabo',
                                revision_date=row_dict.get(
                                    "revision_date", ""
                                ),  # '2010-10-10',
                                ctd_profile_name=row_dict.get(
                                    "profile_file_name_db", ""
                                ),  # 'ctd.profile',
                                dataset_file_name=file_name,
                                ftp_file_path=ftp_file_path,
                            )
                            db_profiles.save()
            #
            return None  # No error message.
        #
        except Exception as e:
            return str(e)

    def splitFilename(self, file_name):
        """ """
        filename = pathlib.Path(file_name).stem
        parts = filename.split("version")
        name = parts[0].strip("_").strip()
        version = parts[1].strip("_").strip() if len(parts) > 0 else ""
        #
        parts = filename.split("_")
        datatype = parts[1].strip("_").strip()
        #
        return name, datatype, version
