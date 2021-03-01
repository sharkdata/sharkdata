#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import json
from django.http import HttpResponse
from django.shortcuts import render
import app_resources.models as models

# import app_sharkdataadmin.models as admin_models
import sharkdata_core

import logging

logger = logging.getLogger(__name__)


def resourceContentText(request, resource_name):
    """ Returns data in text format for a specific resource. """
    logger.debug(
        "Received request for data in text format for resource %s. Request: %s"
        % (resource_name, str(request))
    )

    try:
        resource = models.Resources.objects.get(resource_name=resource_name)
        data_as_text = resource.file_content
        resource_file_name = resource.resource_file_name
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response["Content-Disposition"] = "attachment; filename=" + resource_file_name
        response.write(data_as_text.encode("cp1252"))
        return response
    except Exception as e:
        logger.error(
            "Failed to return data in text for resource %s. Exception: %s"
            % (resource_name, str(e))
        )


def listResources(request):
    """ Generates an HTML page listing all resources. """
    logger.debug(
        "Received request for HTML listing all resources. Request: %s" % (str(request))
    )
    try:
        resources = models.Resources.objects.all().order_by("resource_name")
        #
        return render(request, "list_resources.html", {"resources": resources})
    except Exception as e:
        logger.error(
            "Failed to return HTML listing all resources. Exception: %s" % (str(e))
        )


def listResourcesJson(request):
    """ Generates a JSON file containing a list of resources and their properties. """
    logger.debug(
        "Received request for json-file listing all resources. Request: %s"
        % (str(request))
    )
    try:
        data_header = sharkdata_core.ResourcesUtils().getHeaders()
        resources_json = []
        #
        data_rows = models.Resources.objects.values_list(*data_header)
        for data_row in data_rows:
            row_dict = dict(zip(data_header, data_row))
            resources_json.append(row_dict)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=sharkdata_resource_list.json"
        response.write(json.dumps(resources_json, encoding="utf8"))
        return response
    except Exception as e:
        logger.error(
            "Failed to return json-file listing all resources. Exception: %s" % (str(e))
        )


def tableResourcesText(request):
    """ Generates a text file containing a list of resources and their properties. """
    logger.debug(
        "Received request for text-file listing all resources. Request: %s"
        % (str(request))
    )
    try:
        data_header = sharkdata_core.ResourcesUtils().getResourceListHeaders()
        translated_header = sharkdata_core.ResourcesUtils().translateHeaders(
            data_header
        )
        #
        data_rows = models.Resources.objects.values_list(*data_header)
        #
        response = HttpResponse(content_type="text/plain; charset=cp1252")
        response["Content-Disposition"] = "attachment; filename=sharkdata_resources.txt"
        response.write("\t".join(translated_header) + "\r\n")  # Tab separated.
        for row in data_rows:
            response.write("\t".join(row) + "\r\n")  # Tab separated.
        return response
    except Exception as e:
        logger.error(
            "Failed to return text-file listing all resources. Exception: %s" % (str(e))
        )


def tableResourcesJson(request):
    """Generates a text file containing a list of resources and their properties.
    Organised as header and rows.
    """
    logger.debug(
        "Received request for text-file listing all resources, organised as header and rows. Request: %s"
        % (str(request))
    )
    try:
        data_header = sharkdata_core.ResourcesUtils().getResourceListHeaders()
        #
        data_rows = models.Resources.objects.values_list(*data_header)
        #
        response = HttpResponse(content_type="application/json; charset=cp1252")
        response[
            "Content-Disposition"
        ] = "attachment; filename=sharkdata_resources.json"
        response.write("{")
        response.write('"header": ["')
        response.write('", "'.join(data_header) + '"], ')  # Tab separated.
        response.write(u"'rows': [")
        row_delimiter = ""
        for row in data_rows:
            response.write(row_delimiter + '["' + '", "'.join(row) + '"]')
            row_delimiter = ", "
        response.write("]")
        response.write("}")
        #
        return response
    except Exception as e:
        logger.error(
            "Failed to return text-file listing all resources, organised as header and rows. Exception: %s"
            % (str(e))
        )
