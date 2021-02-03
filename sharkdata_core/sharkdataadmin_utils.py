#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import datetime
from django.conf import settings
import sharkdata_core


@sharkdata_core.singleton
class SharkdataAdminUtils(object):
    """ Singleton class. """

    def __init__(self):
        """ """
        self._update_thread = None
        self._generate_ices_xml_thread = None
        self._validate_ices_xml_thread = None
        # Path to log files for threaded work.
        self._logfile_dir_path = pathlib.Path(settings.SHARKDATA_DATA, "admin_log")

    ##### Log files. #####

    def log_create(self, command, user):
        """ """
        starttime = str(datetime.datetime.now()).replace(":", "")[:17]
        logfile_name = starttime + "_" + command + "_RUNNING.txt"
        logfile_name = logfile_name.replace(" ", "_")
        logfile_path = pathlib.Path(self._logfile_dir_path, logfile_name)

        if not logfile_path.parent.exists():
            logfile_path.parent.mkdir(parents=True)

        with logfile_path.open("w") as logfile:
            logfile.write("\n")
            logfile.write("command: " + command + "\n")
            logfile.write("started_at: " + starttime + "\n")
            logfile.write("user: " + user + "\n")
            logfile.write("\n")

        return logfile_name

    def log_write(self, logfile_name, log_row):
        """ """
        logfile_path = pathlib.Path(self._logfile_dir_path, logfile_name)
        if logfile_path.exists():
            with logfile_path.open("a") as logfile:
                logfile.write(log_row + "\n")

    def log_close(self, logfile_name, new_status):
        """ """
        logfile_path = pathlib.Path(self._logfile_dir_path, logfile_name)
        endtime = str(datetime.datetime.now()).replace(":", "").replace(" ", "_")[:17]
        if logfile_path.exists():
            with logfile_path.open("a") as logfile:
                logfile.write("\n")
                logfile.write("status: " + new_status + "\n")
                logfile.write("finished_at: " + endtime + "\n")
                logfile.write("\n")

            new_file_name = logfile_name.replace("_RUNNING", "_" + new_status.upper())
            new_path = pathlib.Path(self._logfile_dir_path, new_file_name)
            logfile_path.rename(new_path)

    def get_log_files(self):
        """ """
        counter = 0
        log_list = []
        if self._logfile_dir_path.exists():
            for file_name in sorted(
                list(self._logfile_dir_path.glob("*.txt")), reverse=True
            ):
                counter += 1
                if counter <= 100:
                    log_list.append(file_name)
                else:
                    # Remove old files.
                    file_path = pathlib.Path(file_name)
                    if file_path.exists():
                        file_path.unlink()

        return log_list

    def get_log_file_content(self, file_stem):
        """ """
        content = ""
        logfile_path = pathlib.Path(self._logfile_dir_path, file_stem + ".txt")
        if logfile_path.exists():
            with logfile_path.open("r") as logfile:
                content = logfile.read()
        else:
            # Check if status changed.
            parts = file_stem.split("_")
            file_stem_without_status = "_".join(parts[0:-1])
            file_list = list(
                self._logfile_dir_path.glob(file_stem_without_status + "*.txt")
            )
            if len(file_list) > 0:
                file_name = file_list[0]
                logfile_path = pathlib.Path(file_name)
                if logfile_path.exists():
                    with logfile_path.open("r") as logfile:
                        content = logfile.read()

        return content
