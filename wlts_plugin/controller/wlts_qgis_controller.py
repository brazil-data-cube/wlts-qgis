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

import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime

from pyproj import CRS, Proj, transform
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from wlts import WLTS

from ..config import Config


class Controls:
    """Sample controls to main class plugin.

    :methods:
        alert
        formatForQDate
        transformProjection
    """

    def alert(self, type_message, title, text):
        """Show alert message box with a title and info.

        :param title<string>: the message box title.
        :param text<string>: the message box info.
        """
        msg = QMessageBox()
        if type_message == 'error':
            msg.setIcon(QMessageBox.Critical)
        elif type_message == 'warning':
            msg.setIcon(QMessageBox.Warning)
        elif type_message == 'info':
            msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def dialogBox(self, mainDialog, title, text):
        """Create a dialog box to get user info.

        :param mainDialog<string>: the plugin main dialog.
        :param title<string>: the dialog box title.
        :param text<string>: the dialog box info.
        """
        text, okPressed = QInputDialog.getText(mainDialog, title, text, QLineEdit.Normal, "")
        if okPressed and text != "":
            return text
        else:
            return ""

    def formatForQDate(self, date_string):
        """Return a QDate format.

        :param date_string<string>: date string with 'yyyy-mm-dd' format.
        """
        return QDate(
            int(date_string[:4]),
            int(date_string[5:-3]),
            int(date_string[8:])
        )

    def transformProjection(self, projection, latitude, longitude):
        """Transform any projection to EPSG:4326.

        :param projection<string>: string format 'EPSG:4326'.
        :param latitude<float>: the point latitude.
        :param longitude<float>: the point longitude.
        """
        lat, lon = transform(
            Proj(init=CRS.from_string(projection)),
            Proj(init=CRS.from_string("EPSG:4326")),
            latitude, longitude
        )
        return {
            "lat": lat,
            "long": lon,
            "crs": "EPSG:4326"
        }

    def getCollectionDescription(self, server_controls=None, service="", collection=""):
        """Get description from WLTS Server and format for show.

        :param server_controls<Services>: server controls to set services
        :param service<string>: the service name save on server controls
        :param collection<string>: the collection name selected
        """
        metadata = server_controls.description(service, collection)

        classification_system = f'Classification System: ' \
            f'{metadata["classification_system"]["classification_system_name"]}'

        collection_type = f'Collection type: {metadata["collection_type"]}'

        description = f'Description: {metadata["description"]}'

        period = f'Period:\n\tstart date: {metadata["period"]["start_date"]}\n' \
            f'\tend_date: {metadata["period"]["end_date"]}'

        resolution = f'Resolution:\n\tUnit: {metadata["resolution_unit"]["unit"]}\n' \
            f'\tValue: {metadata["resolution_unit"]["value"]}'

        spatial_extent = f'Spatial Extent\n\nmin_x: {metadata["spatial_extent"]["xmin"]:,.2f}\nmax_x: {metadata["spatial_extent"]["xmax"]:,.2f}' \
            f'\nymin: {metadata["spatial_extent"]["ymin"]:,.2f}\nymax: {metadata["spatial_extent"]["ymax"]:,.2f}'

        collection_description = f'{classification_system}\n{collection_type}\n{description}\n{period}' \
            f'\n{resolution}\n{spatial_extent}'

        return collection_description


class WLTS_Controls:
    """Class for the service storage rule.

    :Methods:
        setService
        listProducts
        productDescription
        productTimeSeries
    """

    def __init__(self):
        """Build controls for WLTS Servers."""
        self.wlts_host = Config.WLTS_HOST
        self.wlts = WLTS(self.wlts_host)
        self.trajectory = None

    def getService(self):
        """Get the service data finding by name."""
        return self.wlts_host

    def setService(self, server_host):
        """Edit the service data finding by name.

        :param server_host<string>: the URL service to edit.
        """
        self.wlts_host = server_host
        self.wlts = WLTS(self.getService())

    def listCollections(self):
        """Return a dictionary with the list of available products."""
        return self.wlts.collections

    def description(self, collection_name):
        """Return a dictionary with collection description.

        :param collection_name<string>: the collection name
        """
        return self.wlts[collection_name]

    def getTrajectory(self, lon, lat, collections, start_date, end_date):
        """Plot trajectory with files controls."""
        self.trajectory = self.wlts.tj(
            longitude=lon,
            latitude=lat,
            collections=",".join(collections),
            start_date=start_date,
            end_date=end_date
        )
        return self.trajectory

    def plotTrajectory(self, **parameters):
        """Plotting trajectory using seaborn."""

        # Apply Seaborn grid style globally
        sns.set_theme(style="darkgrid")

        # Default parameters
        parameters.setdefault('marker_size', 10)
        parameters.setdefault('title', 'Land Use and Cover Trajectory')
        parameters.setdefault('title_y', 'Number of Points')
        parameters.setdefault('legend_title_text', 'Class')
        parameters.setdefault('date', 'Year')
        parameters.setdefault('value', 'Collection')
        parameters.setdefault('width', 950)
        parameters.setdefault('height', 320)
        parameters.setdefault('font_size', 12)
        parameters.setdefault('type', 'scatter')
        parameters.setdefault('opacity', 0.8)
        parameters.setdefault('marker_line_width', 1.5)
        parameters.setdefault('bar_title', False)

        # Copy and preprocess
        df = self.trajectory.df().copy()
        df['class'] = df['class'].astype('category')
        df['date'] = df['date'].astype('category')
        df['collection'] = df['collection'].astype('category')

        def update_column_title(title_text):
            new_title = title_text.split("=")[-1].capitalize()
            if len(new_title.split("_")) > 1:
                return new_title.split("_")[0] + " " + new_title.split("_")[-1].capitalize()
            return new_title.split("_")[0]

        # SCATTER PLOT: One point only
        if parameters['type'] == 'scatter':
            if len(df.point_id.unique()) == 1:
                plt.figure(figsize=((parameters['width'] + 200) / 100, parameters['height'] / 100))
                sns.scatterplot(
                    data=df,
                    x='date', y='collection',
                    hue='class', style='class',
                    s=parameters['marker_size']**2,
                    alpha=parameters['opacity'],
                    linewidth=parameters['marker_line_width']
                )
                plt.title(parameters['title'], fontsize=parameters['font_size'])
                plt.xlabel(parameters['date'])
                plt.ylabel(parameters['value'])
                plt.legend(
                    title=parameters['legend_title_text'],
                    bbox_to_anchor=(1.01, 1),
                    loc='upper left',
                    borderaxespad=0
                )
                plt.tight_layout()
                plt.show()
            else:
                raise ValueError("The scatter plot is for one point only! Please try another type: bar plot.")

        # BAR PLOT: Single or multiple collections
        elif parameters['type'] == 'bar':
            if len(df.collection.unique()) == 1 and len(df.point_id.unique()) >= 1:
                df_group = df.groupby(['date', 'class']).count()['point_id'].reset_index()
                df_group.rename(columns={'point_id': 'count'}, inplace=True)

                plt.figure(figsize=((parameters['width'] + 200) / 100, parameters['height'] / 100))
                sns.barplot(
                    data=df_group,
                    x='date', y='count',
                    hue='class',
                    alpha=parameters['opacity']
                )
                plt.title(parameters['title'], fontsize=parameters['font_size'])
                plt.xlabel(parameters['date'])
                plt.ylabel(parameters['title_y'])
                plt.legend(
                    title=parameters['legend_title_text'],
                    bbox_to_anchor=(1.01, 1),
                    loc='upper left',
                    borderaxespad=0
                )
                plt.tight_layout()
                plt.show()

            elif len(df.collection.unique()) >= 1 and len(df.point_id.unique()) >= 1:
                mydf = (
                    df.groupby(['date', 'collection', 'class'])
                    .count()['point_id']
                    .reset_index()
                    .rename(columns={'point_id': 'size'})
                )

                g = sns.catplot(
                    data=mydf,
                    x='date', y='size',
                    hue='class',
                    col='collection',
                    kind='bar',
                    col_wrap=3,
                    height=parameters['height'] / 100,
                    aspect=parameters['width'] / (parameters['height'] * 3),
                    alpha=parameters['opacity']
                )
                g.set_axis_labels(parameters['date'], parameters['title_y'])

                g.add_legend(title=parameters['legend_title_text'])

                # Move legend outside
                g._legend.set_bbox_to_anchor((1.05, 0.5))
                g._legend.set_loc('center left')

                if parameters['bar_title']:
                    for ax in g.axes.flatten():
                        title = ax.get_title()
                        ax.set_title(update_column_title(title))

                plt.tight_layout()
                plt.subplots_adjust(right=0.85)
                plt.show()
        else:
            raise RuntimeError("No plot support for this trajectory!")
