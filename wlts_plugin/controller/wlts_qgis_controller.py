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

from pyproj import CRS, Proj, transform
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from wlts import WLTS

from .config import Config


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
        """Build controls for WTSS Servers."""
        self.wlts_host = Config.WLTS_HOST
        self.wlts = WLTS(self.wlts_host)

    def getService(self):
        """Get the service data finding by name."""
        return self.wlts_host

    def setService(self, server_host):
        """Edit the service data finding by name.

        :param server_host<string>: the URL service to edit.
        """
        self.wlts_host = server_host
        self.wtss = WLTS(self.getService())

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
        return self.wlts.tj(
            longitude=lon,
            latitude=lat,
            collections=",".join(collections),
            start_date=start_date,
            end_date=end_date
        )
