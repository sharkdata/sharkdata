#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://sharkdata.smhi.se
# Copyright (c) 2018-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import datetime
import pathlib
import folium
import bokeh

# from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

from app_ctdprofiles import ctd_profile_plot


class CtdProfilesCore:
    """ """

    def __init__(self):
        """ """

    def createMap(self, lat_long_desc_table=[]):
        """ Plots positions on an interactive OpenStreetMap by using the folium library. """
        m = folium.Map([60.0, 15.0], zoom_start=5)
        test = folium.Html("<b>Hello world</b>", script=True)
        popup = folium.Popup(test, max_width=2650)

        # TEST DATA.
        if not lat_long_desc_table:
            lat_long_desc_table = [
                #                 [55.6175, 14.8675, 'Svea-2019-1111'],
                #                 [60.0, 20.0, 'Svea-2019-1222'],
            ]

        #
        for lat, long, desc in lat_long_desc_table:
            marker = folium.Marker([lat, long], popup=desc).add_to(m)

        return m.get_root().render()

    def createPlot(self, path_zipfile, profile_name):
        """ Plots ... """
        rzip = ctd_profile_plot.ReadZipFile(path_zipfile, profile_name)

        parameter_list = [
            "PRES_CTD [dbar]",
            "CNDC_CTD [S/m]",
            "CNDC2_CTD [S/m]",
            "SALT_CTD [psu (PSS-78)]",
            "SALT2_CTD [psu (PSS-78)]",
            "TEMP_CTD [°C (ITS-90)]",
            "TEMP2_CTD [°C (ITS-90)]",
            "DOXY_CTD [ml/l]",
            "DOXY2_CTD [ml/l]",
            "PAR_CTD [µE/(cm2 ·sec)]",
            "CHLFLUO_CTD [mg/m3]",
            "TURB_CTD [NTU]",
            "PHYC_CTD [ppb]",
        ]

        data = rzip.get_data(parameter_list)

        profile = ctd_profile_plot.ProfilePlot(data, parameters=parameter_list)
        plot = profile.plot(
            x="TEMP_CTD [°C (ITS-90)]",
            y="PRES_CTD [dbar]",
            z="SALT_CTD [psu (PSS-78)]",
            name=profile_name,
        )

        html = file_html(plot, CDN, "my plot")
        return html

    def downloadProfile(self, path_zipfile, profile_name):
        """ Plots ... """
        rzip = ctd_profile_plot.ReadZipFile(path_zipfile, profile_name)

        parameter_list = [
            "PRES_CTD [dbar]",
            "CNDC_CTD [S/m]",
            "CNDC2_CTD [S/m]",
            "SALT_CTD [psu (PSS-78)]",
            "SALT2_CTD [psu (PSS-78)]",
            "TEMP_CTD [°C (ITS-90)]",
            "TEMP2_CTD [°C (ITS-90)]",
            "DOXY_CTD [ml/l]",
            "DOXY2_CTD [ml/l]",
            "PAR_CTD [µE/(cm2 ·sec)]",
            "CHLFLUO_CTD [mg/m3]",
            "TURB_CTD [NTU]",
            "PHYC_CTD [ppb]",
        ]

        data = rzip.get_data(parameter_list)

        profile = ctd_profile_plot.ProfilePlot(data, parameters=parameter_list)
        plot = profile.plot(
            x="TEMP_CTD [°C (ITS-90)]",
            y="PRES_CTD [dbar]",
            z="SALT_CTD [psu (PSS-78)]",
            name=profile_name,
        )

        html = file_html(plot, CDN, "my plot")
        return html
