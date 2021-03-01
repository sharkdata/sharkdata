# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponse
import django.core.paginator as paginator

from . import ctdprofiles_core
from app_ctdprofiles import models

import urllib.parse

import logging

logger = logging.getLogger(__name__)


def listCtdProfiles(request):
    """ Generates an HTML page listing all datasets. """

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
    #

    years = (
        models.CtdProfiles.objects.values_list("visit_year", flat=True)
        .distinct()
        .order_by("-visit_year")
    )
    projects = (
        models.CtdProfiles.objects.values_list("sample_project_code", flat=True)
        .distinct()
        .order_by("sample_project_code")
    )
    platforms = (
        models.CtdProfiles.objects.values_list("platform_code", flat=True)
        .distinct()
        .order_by("platform_code")
    )

    last_year = years[0] if len(years) > 0 else ""

    selected_year = request.GET.get("year", last_year)
    selected_project = request.GET.get("project", "")
    selected_platform = request.GET.get("platform", "")
    selected_date = request.GET.get("date", "")
    #     selected_revision_date_after = request.GET.get('revision_date_after', '')
    selected_latitude_from = request.GET.get("latitude_from", "")
    selected_latitude_to = request.GET.get("latitude_to", "")
    selected_longitude_from = request.GET.get("longitude_from", "")
    selected_longitude_to = request.GET.get("longitude_to", "")
    selected_station = request.GET.get("station", "")

    try:
        selected_latitude_from = float(
            urllib.parse.unquote_plus(selected_latitude_from)
        )
    except:
        pass
    try:
        selected_latitude_to = float(urllib.parse.unquote_plus(selected_latitude_to))
    except:
        pass
    try:
        selected_longitude_from = float(
            urllib.parse.unquote_plus(selected_longitude_from)
        )
    except:
        pass
    try:
        selected_longitude_to = float(urllib.parse.unquote_plus(selected_longitude_to))
    except:
        pass

    db_filter_dict = {}
    if selected_year not in ["", "All", 'selected="selected"']:
        db_filter_dict[
            "{0}__{1}".format("visit_year", "iexact")
        ] = urllib.parse.unquote_plus(selected_year)
    if selected_project not in ["", "All"]:
        db_filter_dict[
            "{0}__{1}".format("sample_project_code", "iexact")
        ] = urllib.parse.unquote_plus(selected_project)
    if selected_platform not in ["", "All"]:
        db_filter_dict[
            "{0}__{1}".format("platform_code", "iexact")
        ] = urllib.parse.unquote_plus(selected_platform)
    if selected_date not in [
        "",
    ]:
        db_filter_dict[
            "{0}__{1}".format("sample_date", "iexact")
        ] = urllib.parse.unquote_plus(selected_date)
    if selected_latitude_from not in [
        "",
    ]:
        db_filter_dict["{0}__{1}".format("latitude", "gte")] = selected_latitude_from
    if selected_latitude_to not in [
        "",
    ]:
        db_filter_dict["{0}__{1}".format("latitude", "lte")] = selected_latitude_to
    if selected_longitude_from not in [
        "",
    ]:
        db_filter_dict["{0}__{1}".format("longitude", "gte")] = selected_longitude_from
    if selected_longitude_to not in [
        "",
    ]:
        db_filter_dict["{0}__{1}".format("longitude", "lte")] = selected_longitude_to
    if selected_station not in [
        "",
    ]:
        db_filter_dict[
            "{0}__{1}".format("station_name", "icontains")
        ] = urllib.parse.unquote_plus(selected_station)
    #     if selected_revision_date_after not in ['', ]:
    #         db_filter_dict['{0}__{1}'.format('revision_date', 'gte')] = urllib.parse.unquote_plus(selected_revision_date_after)

    #
    #     if (selected_datatype and (selected_datatype != 'All')):
    #         datasets = models.Datasets.objects.all().filter(datatype = selected_datatype).order_by('dataset_name')
    #     else:
    #         datasets = models.Datasets.objects.all().order_by('dataset_name')

    ctdprofiles = models.CtdProfiles.objects.filter(**db_filter_dict).order_by(
        "visit_year", "platform_code", "visit_id"
    )

    # <td>{{ ctdprofile.visit_year }}</td>
    # <td>{{ ctdprofile.platform_code }}</td>
    # <td>{{ ctdprofile.visit_id }}</td>
    #
    # <td>{{ ctdprofile.station_name }}</td>
    # <td>{{ ctdprofile.sample_date }}</td>
    # <td>{{ ctdprofile.latitude }}</td>
    # <td>{{ ctdprofile.longitude }}</td>
    # <td>{{ ctdprofile.water_depth_m }}</td>
    #
    # <td>{{ ctdprofile.sample_project_code }}</td>
    # <td>{{ ctdprofile.sample_orderer_code }}</td>
    # <td>{{ ctdprofile.revision_date }}</td>
    # <td>{{ ctdprofile.ctd_profile_name }}</td>
    #
    # <td>{{ ctdprofile.dataset_file_name }}</td>

    #     #
    #     datatypes = models.Datasets.objects.values_list('datatype').distinct().order_by('datatype')
    #     datatype_list = []
    #     for datatype in datatypes:
    #         try:
    #             datatype_list.append(datatype[0])
    #         except:
    #             pass
    #

    lat_long_desc_table = []
    for db_row in ctdprofiles:
        lat_long_desc_table.append(
            [
                db_row.latitude,
                db_row.longitude,
                db_row.platform_code,
            ]
        )
    #
    ctd = ctdprofiles_core.CtdProfilesCore()
    map_html = ctd.createMap(lat_long_desc_table)

    #
    pag = paginator.Paginator(ctdprofiles, pagination_size)
    pagination_page = pagination_page if pagination_page <= pag.num_pages else 1
    try:
        ctdprofiles_page = pag.page(pagination_page)
    except paginator.EmptyPage:
        ctdprofiles_page = []  # If page is out of range, return empty list.
    #
    number_of_rows = len(ctdprofiles)
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
        "list_ctdprofiles.html",
        {
            "row_info": row_info,
            "page": pagination_page,
            "per_page": pagination_size,
            "prev_page": prev_page,
            "next_page": next_page,
            "pages": pag.num_pages,
            "years": years,
            "selected_year": selected_year,
            "projects": projects,
            "selected_project": selected_project,
            "platforms": platforms,
            "selected_platform": selected_platform,
            "selected_date": selected_date,
            #                                'selected_revision_date_after' : selected_revision_date_after,
            "selected_latitude_from": selected_latitude_from,
            "selected_latitude_to": selected_latitude_to,
            "selected_longitude_from": selected_longitude_from,
            "selected_longitude_to": selected_longitude_to,
            "selected_station": selected_station,
            "ctdprofiles": ctdprofiles_page,
            "map_html": map_html,
            "selected_datatype": "All",  # TODO:
        },
    )


def listCtdProfilesJson(request):
    """ Generates a JSON file containing a list of datasets and their properties. """


#     data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
#     datasets_json = []
#     #
#     data_rows = models.Datasets.objects.values_list(*data_header)
#     for data_row in data_rows:
#         row_dict = dict(zip(data_header, map(unicode, data_row)))
#         datasets_json.append(row_dict)
#     #
#     response = HttpResponse(content_type = 'application/json; charset=cp1252')
#     response['Content-Disposition'] = 'attachment; filename=sharkdata_dataset_list.json'
#     response.write(json.dumps(datasets_json, encoding = 'utf8'))
#     return response


def viewTestMap(request, profile_name):
    """ """
    lat_long_desc_table = []
    ctdprofiles = models.CtdProfiles.objects.filter(ctd_profile_name=profile_name)
    for db_row in ctdprofiles:
        row = [
            db_row.latitude,
            db_row.longitude,
            db_row.station_name + "\n" + db_row.sample_date,
        ]
        lat_long_desc_table.append(row)

    ctd = ctdprofiles_core.CtdProfilesCore()

    return HttpResponse(content=ctd.createMap(lat_long_desc_table))


def viewTestPlot(request, profile_name):
    """ """
    ctdprofiles = models.CtdProfiles.objects.filter(ctd_profile_name=profile_name)
    for db_row in ctdprofiles:
        ftp_file_path = db_row.ftp_file_path
        ctd_profile_name = db_row.ctd_profile_name

        ctd = ctdprofiles_core.CtdProfilesCore()
        return HttpResponse(content=ctd.createPlot(ftp_file_path, ctd_profile_name))


#     ctd = ctdprofiles_core.CtdProfilesCore()
#
#     return HttpResponse(content = ctd.createPlot('aaa', 'bbb'))


def downloadTestPlot(request, profile_name):
    """ """

    logger.debug(
        "Received request for downloading test plot, for profile %s. Request: %s"
        % (profile_name, str(request))
    )

    try:
        lat_long_desc_table = []
        ctdprofiles = models.CtdProfiles.objects.filter(ctd_profile_name=profile_name)
        for db_row in ctdprofiles:
            row = [
                db_row.latitude,
                db_row.longitude,
                db_row.station_name + "\n" + db_row.sample_date,
            ]
            lat_long_desc_table.append(row)

        ctd = ctdprofiles_core.CtdProfilesCore()

        logger.info("Returning test plot for downloading. Profile %s." % (profile_name))

        return HttpResponse(content=ctd.createMap(lat_long_desc_table))
    except Exception as e:
        logger.error(
            "Failed to return test plot for downloading. Requested profile: %s. Exception: %s"
            % (profile_name, str(e))
        )
