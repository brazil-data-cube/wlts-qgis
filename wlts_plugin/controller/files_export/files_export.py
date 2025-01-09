#
# This file is part of Python QGIS Plugin for WLTS.
# Copyright (C) 2025 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

import csv
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class FilesExport:
    """Exporting WLTS data in different formats.

    :Methods:
        defaultCode
        generateCode
        generateCSV
        generateJSON
        generatePlotFIG
    """

    def defaultCode(self):
        """Return a default python code with blank WLTS parameters."""
        template = (
            Path(os.path.abspath(os.path.dirname(__file__)))
                / 'examples'
                    / 'trajectory_export_template.txt'
        )
        return open(template, 'r').read()

    def generateCode(self, file_name, attributes):
        """Generate a python code file filling WLTS blank spaces.

        :param file_name<str>: file to save path
        :param attributtes<dict>: {
            "host"<str>: the chosen WLTS host
            "collections"<tuple>: the list of selected bands
            "coordinates"<dict>: {
                "crs"<str>: the projection of Latitude and Longitude of Point
                "lat"<float>: selected Latitude
                "long"<float>: selected Longitude
            }
            "time_interval"<dict>: {
                "start_date"<str>: defining start of time interval in string format <yyyy-MM-dd>
                "end_date"<str>: defining end of time interval in string format <yyyy-MM-dd>
            }
        }
        """
        try:
            lat = "{:,.2f}".format(attributes.get("lat"))
            lon = "{:,.2f}".format(attributes.get("long"))
            mapping = {
                "service_host": attributes.get("host"),
                "collections": attributes.get("collections"),
                "geometry": attributes.get("geometry"),
                "latitude": lat,
                "longitude": lon,
                "start_date": attributes.get("start"),
                "end_date": attributes.get("end")
            }
            code_to_save = self.defaultCode().format(**mapping)
            file = open(file_name, "w")
            file.write(code_to_save)
            file.close()
        except FileNotFoundError:
            pass

    def generateCSV(self, file_name, trajectory):
        """Generate a CSV file with trajectory data.

        :param file_name<str>: file to save path.
        :param trajectory<dict>: the trajectory reponse dictionary.
        """
        try:
            df = trajectory.df()
            dict = {}
            latlng = [
                trajectory.get('query').get('latitude'),
                trajectory.get('query').get('longitude')
            ]
            for key in list(df.keys()):
                line = []
                for i in range(len(df[key])):
                    line.append(df[key][i])
                dict[key] = line
            latitude = []
            longitude = []
            for i in range(len(df)):
                latitude.append(latlng[0])
                longitude.append(latlng[1])
            dict['latitude'] = latitude
            dict['longitude'] = longitude
            output = pd.DataFrame.from_dict(dict)
            output.to_csv(file_name, sep=';', index=False, header=True)
        except FileNotFoundError:
            pass

    def generateJSON(self, file_name, trajectory):
        """Generate a JSON file with trajectory data.

        :param file_name<str>: file to save path.
        :param trajectory<dict>: the trajectory service reponse dictionary.
        """
        try:
            with open(file_name, 'w') as outfile:
                json.dump(trajectory, outfile)
        except FileNotFoundError:
            pass

    def generatePlotFig(self, trajectory):
        """Generate an image .JPEG with trajectory data in a table.

        :param trajectory<dict>: the trajectory service reponse dictionary.
        """
        try:
            plt.clf()
            plt.cla()
            plt.close()
            fig = plt.figure(figsize=(12, 5))
            df_trajectory = trajectory.df().drop(columns="geom")
            ax2 = fig.add_subplot()
            font_size = 11
            bbox = [0, 0, 1, 1]
            ax2.axis('off')
            mpl_table = ax2.table(
                cellText=df_trajectory.values,
                rowLabels=df_trajectory.index,
                bbox=bbox,
                colLabels=df_trajectory.columns
            )
            mpl_table.auto_set_font_size(False)
            mpl_table.set_fontsize(font_size)
            plt.show()
        except:
            pass
