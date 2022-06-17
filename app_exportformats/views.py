#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import json

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.core import paginator
from app_exportformats import models
from wsgiref.util import FileWrapper
import os

import logging

logger = logging.getLogger(__name__)

EXPORT_FILES_LIST_HEADER = [
        "format",
        "generated_by",
        "datatype",
        "year",
        "status",
        "approved",
        "export_name",
        "export_file_name",
        "generated_datetime",
    ]

def downloadExportFile(request, exportformat_name):
    """ Returns the export format file. """

    logger.debug(
        "Request for export format file %s received. Request: %s"
        % (exportformat_name, str(request))
    )

    try:
        #
        export_file = models.ExportFiles.objects.get(export_name=exportformat_name)

        file_path = export_file.export_file_path
        
        file_extension = os.path.splitext(file_path)[1]

        #
        wrapper = FileWrapper(open(file_path, "rb"))
        response = StreamingHttpResponse(wrapper, content_type="application/%s" % (file_extension))
        response["Content-Disposition"] = "attachment; filename=%s" % export_file
        response["Content-Length"] = os.path.getsize(file_path)
        #

        logger.info("Returning export format file %s." % (exportformat_name))
        return response
    except Exception as e:
        logger.error(
            "Failed to return export format file %s. Exception: %s"
            % (exportformat_name, str(e))
        )
        
def downloadLogFile(request, exportformat_name):
    """ Returns the export format file. """

    logger.debug(
        "Request for export format file %s received. Request: %s"
        % (exportformat_name, str(request))
    )

    try:
        #
        log_file = models.ExportFiles.objects.get(export_name=exportformat_name)

        file_name = log_file.error_log_file
        file_path = log_file.error_log_file_path
        #
        wrapper = FileWrapper(open(file_path, "rb"))
        response = StreamingHttpResponse(wrapper, content_type="application/txt")
        response["Content-Disposition"] = "attachment; filename=%s" % file_name
        response["Content-Length"] = os.path.getsize(file_path)
        #

        logger.info("Returning export format file %s." % (exportformat_name))
        return response
    except Exception as e:
        logger.error(
            "Failed to return export format file %s. Exception: %s"
            % (exportformat_name, str(e))
        )

def listExportFiles(request):
    """ Generates an HTML page listing all ExportFiles. """

    # URL parameters.
    per_page_default = 10
    try:
        pagination_page = int(request.GET.get("page", 1))
    except:
        pagination_page = 1
    try:
        pagination_size = int(request.GET.get("per_page", per_page_default))
    except:
        pagination_size = per_page_default
    selected_format = request.GET.get("format", "All")
    #
    if selected_format and (selected_format != "All"):
        #         exportfiles = models.ExportFiles.objects.all().filter(format = selected_format).order_by('export_file_name')
        exportfiles = (
            models.ExportFiles.objects.all()
            .filter(format=selected_format)
            .order_by("-generated_datetime")
        )
    else:
        #         exportfiles = models.ExportFiles.objects.all().order_by('export_file_name')
        exportfiles = models.ExportFiles.objects.all().order_by("-generated_datetime")
    #
    formats = (
        models.ExportFiles.objects.values_list("format").distinct().order_by("format")
    )
    format_list = []
    for format_item in formats:
        try:
            format_list.append(format_item[0])
        except:
            pass
    #
    pag = paginator.Paginator(exportfiles, pagination_size)
    pagination_page = pagination_page if pagination_page <= pag.num_pages else 1
    try:
        exportfiles_page = pag.page(pagination_page)
    except paginator.EmptyPage:
        exportfiles_page = []  # If page is out of range, return empty list.
    #
    number_of_rows = len(exportfiles)
    first_row = (pagination_page - 1) * pagination_size + 1
    last_row = first_row + pagination_size - 1
    last_row = last_row if last_row <= number_of_rows else number_of_rows
    row_info = (
        u"Row " + str(first_row) + " - " + str(last_row) + " of " + str(number_of_rows)
    )
    prev_page = pagination_page - 1 if pagination_page > 1 else pagination_page
    next_page = (
        pagination_page + 1 if pagination_page < pag.num_pages else pagination_page
    )

    return render(
        request,
        "list_exportfiles.html",
        {
            "row_info": row_info,
            "page": pagination_page,
            "per_page": pagination_size,
            "prev_page": prev_page,
            "next_page": next_page,
            "pages": pag.num_pages,
            "formats": format_list,
            "selected_format": selected_format,
            "exportfiles": exportfiles_page,
        },
    )


def listExportFilesJson(request):
    """ Generates a JSON file containing a list of exportfiles and their properties. """
    data_rows, data_header = _getExportFilesData()
    
    exportfiles_json = []
    for data_row in data_rows:
        row_dict = dict(zip(data_header, map(str, data_row)))
        exportfiles_json.append(row_dict)
    #
    response = HttpResponse(content_type="application/json; charset=utf8")
    response[
        "Content-Disposition"
    ] = "attachment; filename=sharkdata_exportfile_list.json"
    response.write(json.dumps(exportfiles_json))
    return response


def tableExportFilesText(request):
    """ Generates a text file containing a list of exportfiles and their properties. """
    data_rows, data_header = _getExportFilesData()
    
    response = HttpResponse(content_type="text/plain; charset=cp1252")
    response["Content-Disposition"] = "attachment; filename=sharkdata_exportfiles.txt"
    response.write("\t".join(data_header) + "\r\n")  # Tab separated.
    for row in data_rows:
        response.write("\t".join(map(str, row)) + "\r\n")  # Tab separated.
    return response


def tableExportFilesJson(request):
    """Generates a text file containing a list of exportfiles and their properties.
    Organised as header and rows.
    """

    data_rows, data_header = _getExportFilesData()

    response = HttpResponse(content_type="application/json; charset=cp1252")
    response["Content-Disposition"] = "attachment; filename=sharkdata_exportfiles.json"
    response.write("{")
    response.write('"header": ["')
    response.write('", "'.join(data_header) + '"], ')  # Tab separated.
    response.write('"rows": [')
    row_delimiter = ""
    for row in data_rows:
        response.write(row_delimiter + '["' + '", "'.join(map(str, row)) + '"]')
        row_delimiter = ", "
    response.write("]")
    response.write("}")
    #
    return response

def _getExportFilesData():
    data_header = EXPORT_FILES_LIST_HEADER
    return models.ExportFiles.objects.values_list(*data_header), data_header
