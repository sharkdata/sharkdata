#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import json
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from wsgiref.util import FileWrapper
import django.core.paginator as paginator
import app_datasets.models as models

import sharkdata_core

import logging

logger = logging.getLogger(__name__)


def datasetDataText(request, dataset_name):
    """ Returns data in text format for a specific dataset. """

    logger.debug(
        "Received request for data in text format for dataset %s. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        #
        header_language = request.GET.get("header_language", None)
        #
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        data_as_text = sharkdata_core.DatasetUtils().getDataAsText(dataset_name)
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(".zip", ".txt")
        if header_language:
            # Extract first row and translate.
            rows = data_as_text.split("\r\n")
            if len(rows) > 0:
                headerrow = sharkdata_core.DatasetUtils().translateDataHeaders(
                    rows[0].split("\t"), language=header_language
                )
                response.write(("\t".join(headerrow) + "\r\n").encode("cp1252"))
            if len(rows) > 0:
                response.write("\r\n".join(rows[1:]).encode("cp1252"))
        else:
            response.write(data_as_text.encode("cp1252"))
        #

        logger.info("Returning data in text format for dataset %s." % (dataset_name))
        return response
    except Exception as e:
        logger.error(
            "Failed to generate data in text format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def datasetDataJson(request, dataset_name):
    """ Returns data in JSON format for a specific dataset. """

    logger.debug(
        "Received request for data in json format for dataset %s. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        #
        header_language = request.GET.get("header_language", None)
        #
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        data_as_text = sharkdata_core.DatasetUtils().getDataAsText(dataset_name)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(".zip", ".json")
        response.write("{")
        row_delimiter = ""
        #     for index, row in enumerate(data_as_text.split('\r\n')):
        for index, row in enumerate(data_as_text.split("\n")):
            rowitems = row.strip().split("\t")
            if index == 0:
                response.write('"header": ["')
                if header_language:
                    rowitems = sharkdata_core.DatasetUtils().translateDataHeaders(
                        rowitems, language=header_language
                    )
                #
                outrow = '", "'.join(rowitems) + '"], '
                #
                response.write(outrow.encode("cp1252"))
                response.write(' "rows": [')
            else:
                if len(rowitems) > 1:
                    outrow = row_delimiter + '["' + '", "'.join(rowitems) + '"]'
                    response.write(outrow.encode("cp1252"))
                    row_delimiter = ", "
        response.write("]")
        response.write("}")
        #

        logger.info("Returning data in json format for dataset %s." % (dataset_name))
        return response
    except Exception as e:
        logger.error(
            "Failed to generate data in json format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def datasetDataColumnsText(request, dataset_name):
    """Returns data in text format for a specific dataset.
    Column format.
    """

    logger.debug(
        "Request for data in text-based column format for dataset %s received. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        #
        header_language = request.GET.get("header_language", None)
        #
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        data_as_text = sharkdata_core.DatasetUtils().getDataColumnsAsText(dataset_name)
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(".zip", "_COLUMNS.txt")
        if header_language:
            # Extract first row and translate.
            rows = data_as_text.split("\r\n")
            if len(rows) > 0:
                headerrow = sharkdata_core.DatasetUtils().translateDataHeaders(
                    rows[0].split("\t"), language=header_language
                )
                response.write(("\t".join(headerrow) + "\r\n").encode("cp1252"))
            if len(rows) > 0:
                response.write("\r\n".join(rows[1:]).encode("cp1252"))
        else:
            response.write(data_as_text.encode("cp1252"))
        #

        logger.info(
            "Returning data in text-based column format for dataset %s."
            % (dataset_name)
        )
        return response
    except Exception as e:
        logger.error(
            "Failed to generate data in text-based column format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def datasetDataColumnsJson(request, dataset_name):
    """Returns data in JSON format for a specific dataset.
    Column format.
    """

    logger.debug(
        "Request for data in json-based column format for dataset %s received. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        #
        header_language = request.GET.get("header_language", None)
        #
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        data_as_text = sharkdata_core.DatasetUtils().getDataColumnsAsText(dataset_name)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(".zip", "_COLUMNS.json")
        response.write("{")
        row_delimiter = ""
        #     for index, row in enumerate(data_as_text.split('\r\n')):
        for index, row in enumerate(data_as_text.split("\n")):
            rowitems = row.strip().split("\t")
            if index == 0:
                response.write('"header": ["')
                if header_language:
                    rowitems = sharkdata_core.DatasetUtils().translateDataHeaders(
                        rowitems, language=header_language
                    )
                #
                outrow = '", "'.join(rowitems) + '"], '
                response.write(outrow.encode("cp1252"))
                response.write(' "rows": [')
            else:
                if len(rowitems) > 1:
                    outrow = row_delimiter + '["' + '", "'.join(rowitems) + '"]'
                    response.write(outrow.encode("cp1252"))
                    row_delimiter = ", "
        response.write("]")
        response.write("}")
        #

        logger.info(
            "Returning data in json-based column format for dataset %s."
            % (dataset_name)
        )
        return response
    except Exception as e:
        logger.error(
            "Failed to generate data in json-based column format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def datasetMetadataText(request, dataset_name):
    """ Returns metadata in text format for a specific dataset. """

    logger.debug(
        "Request for meta-data in text format for dataset %s received. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        metadata_as_text = sharkdata_core.DatasetUtils().getMetadataAsText(dataset_name)
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(".zip", "_METADATA.txt")
        response.write(metadata_as_text)

        logger.info(
            "Returning meta-data in text format for dataset %s." % (dataset_name)
        )
        return response
    except Exception as e:
        logger.error(
            "Failed to generate meta-data in text format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def datasetMetadataJson(request, dataset_name):
    """ Returns metadata in JSON format for a specific dataset. """

    logger.debug(
        "Request for meta-data in json format for dataset %s received. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        #
        metadata_as_text = sharkdata_core.DatasetUtils().getMetadataAsText(dataset_name)
        metadata_dict = {}
        for row in metadata_as_text.split("\r\n"):
            if ":" in row:
                parts = row.split(":", 1)  # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_dict[key] = value
        #
        response = HttpResponse(content_type="application/json; charset=utf-8")
        response[
            "Content-Disposition"
        ] = "attachment; filename=" + dataset_file_name.replace(
            ".zip", "_METADATA.json"
        )
        response.write(json.dumps(metadata_dict))

        logger.info(
            "Returning meta-data in json format for dataset %s." % (dataset_name)
        )
        return response
    except Exception as e:
        logger.error(
            "Failed to generate meta-data in json format for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


def sharkArchiveZip(request, dataset_name):
    """ Returns the SHARK Archive file. """

    logger.debug(
        "Request for SHARK archive file for dataset %s received. Request: %s"
        % (dataset_name, str(request))
    )

    try:
        #
        dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        dataset_file_name = dataset.dataset_file_name
        ftp_file_path = dataset.ftp_file_path
        #
        wrapper = FileWrapper(open(ftp_file_path, "rb"))
        response = StreamingHttpResponse(wrapper, content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=%s" % dataset_file_name
        response["Content-Length"] = os.path.getsize(ftp_file_path)
        #

        logger.info("Returning SHARK archive file for dataset %s." % (dataset_name))
        return response
    except Exception as e:
        logger.error(
            "Failed to return SHARK archive file for dataset %s. Exception: %s"
            % (dataset_name, str(e))
        )


##############################################################################################################


def listDatasets(request):
    """ Generates an HTML page listing all datasets. """

    logger.debug(
        "Request for complete dataset list received. Request: %s" % (str(request))
    )

    try:
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
        selected_datatype = request.GET.get("datatype", "All")
        #
        if selected_datatype and (selected_datatype != "All"):
            datasets = (
                models.Datasets.objects.all()
                .filter(datatype=selected_datatype)
                .order_by("dataset_name")
            )
        else:
            datasets = models.Datasets.objects.all().order_by("dataset_name")
        #
        datatypes = (
            models.Datasets.objects.values_list("datatype")
            .distinct()
            .order_by("datatype")
        )
        datatype_list = []
        for datatype in datatypes:
            try:
                datatype_list.append(datatype[0])
            except:
                pass
        #
        pag = paginator.Paginator(datasets, pagination_size)
        pagination_page = pagination_page if pagination_page <= pag.num_pages else 1
        try:
            datasets_page = pag.page(pagination_page)
        except paginator.EmptyPage:
            datasets_page = []  # If page is out of range, return empty list.
        #
        number_of_rows = len(datasets)
        first_row = (pagination_page - 1) * pagination_size + 1
        last_row = first_row + pagination_size - 1
        last_row = last_row if last_row <= number_of_rows else number_of_rows
        row_info = (
            u"Row "
            + str(first_row)
            + " - "
            + str(last_row)
            + " of "
            + str(number_of_rows)
        )
        prev_page = pagination_page - 1 if pagination_page > 1 else pagination_page
        next_page = (
            pagination_page + 1 if pagination_page < pag.num_pages else pagination_page
        )

        logger.info(
            "Returning html with list of datasets. Page no: %i, page size: %i, selected_datatype: %s"
            % (pagination_page, pagination_size, selected_datatype)
        )

        return render(
            request,
            "list_datasets.html",
            {
                "row_info": row_info,
                "page": pagination_page,
                "per_page": pagination_size,
                "prev_page": prev_page,
                "next_page": next_page,
                "pages": pag.num_pages,
                "datatypes": datatype_list,
                "selected_datatype": selected_datatype,
                "datasets": datasets_page,
            },
        )

    except Exception as e:
        logger.error("Failed to list datasets. Exception: %s" % (str(e)))


def listDatasetsJson(request):
    """ Generates a JSON file containing a list of datasets and their properties. """

    logger.debug(
        "Request for complete dataset list in json format received. Request: %s"
        % (str(request))
    )

    try:
        data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
        datasets_json = []
        #
        data_rows = models.Datasets.objects.values_list(*data_header)
        for data_row in data_rows:
            row_dict = dict(zip(data_header, map(str, data_row)))
            datasets_json.append(row_dict)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=sharkdata_dataset_list.json"
        response.write(json.dumps(datasets_json))

        logger.info("Returning complete dataset list in json format.")
        return response
    except Exception as e:
        logger.error(
            "Failed to generate complete dataset list in json format! Exception: %s"
            % (str(e))
        )


def tableDatasetsText(request):
    """ Generates a text file containing a list of datasets and their properties. """

    logger.debug(
        "Request for complete dataset list in text format received. Request: %s"
        % (str(request))
    )

    try:
        header_language = request.GET.get("header_language", None)
        data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
        translated_header = sharkdata_core.DatasetUtils().translateDatasetListHeaders(
            data_header, language=header_language
        )
        #
        data_rows = models.Datasets.objects.values_list(*data_header)
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response["Content-Disposition"] = "attachment; filename=sharkdata_datasets.txt"
        response.write("\t".join(translated_header) + "\r\n")  # Tab separated.
        for row in data_rows:
            response.write("\t".join(map(str, row)) + "\r\n")  # Tab separated.

        logger.info("Returning complete dataset list in text format.")

        return response
    except Exception as e:
        logger.error(
            "Failed to return complete dataset list in text format. Exception: %s"
            % (str(e))
        )


def tableDatasetsJson(request):
    """Generates a text file containing a list of datasets and their properties.
    Organised as header and rows.
    """

    logger.debug(
        "Request for complete dataset list in json format received. Request: %s"
        % (str(request))
    )

    try:
        data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
        #
        data_rows = models.Datasets.objects.values_list(*data_header)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response["Content-Disposition"] = "attachment; filename=sharkdata_datasets.json"
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

        logger.info(
            "Returning complete dataset list in json format. Organised as header and rows."
        )

        return response
    except Exception as e:
        logger.error(
            "Failed to return complete dataset list in json format. Exception: %s"
            % (str(e))
        )
