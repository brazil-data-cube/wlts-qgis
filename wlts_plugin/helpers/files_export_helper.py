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

import json
import os
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from wlts import WLTS

from ..config import Config
from ..controller.wlts_qgis_controller import Controls, WLTS_Controls


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

    def defaultImage(self):
        return f'{Config.BASE_DIR}/wlts_plotly.png'

    def getExportOptions(self):
        """Set options to export result."""
        return [
            "CSV", "JSON",
            "Python", "Plotly"
        ]

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
            lat = attributes.get("lat")
            lon = attributes.get("long")
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

    def generatePlotFig(self, wlts_controls: WLTS_Controls):
        """Generate an image .JPEG with trajectory data in a table.

        :param trajectory<dict>: the trajectory service reponse dictionary.
        """
        try:
            wlts_controls.plotTrajectory(
                marker_size=8, font_size=12,
                width=1050, height=320
            )
        except Exception as e:
            controls = Controls()
            controls.alert("error", "Error while generate an image!", str(e))

    def generatePlotlyFig(self, wlts_controls: WLTS_Controls):
        """Generate an SVG based on Plotly with trajectory data in a table.

        :param trajectory<dict>: the trajectory service reponse dictionary.
        """
        try:
            fig = WLTS.plot(
                wlts_controls.trajectory.df(),
                marker_size=8, font_size=12,
                width=1050, height=320
            )
            fig.show()
        except Exception as e:
            controls = Controls()
            controls.alert("error", "Error while generate an image!", str(e))
