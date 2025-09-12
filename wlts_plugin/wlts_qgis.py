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

from datetime import datetime
import json
import os.path
import time
from pathlib import Path

import qgis.utils
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import (QgsCoordinateReferenceSystem, QgsFeature, QgsPoint,
                       QgsProject, QgsRasterMarkerSymbolLayer, QgsRectangle,
                       QgsSingleSymbolRenderer, QgsSymbol, QgsVectorLayer,
                       QgsWkbTypes)
from qgis.gui import QgsMapToolEmitPoint, QgsMapToolPan
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .config import Config
# Import files exporting controls
from .helpers.files_export_helper import FilesExport
# Import the controls for the plugin
from .controller.wlts_qgis_controller import Controls, WLTS_Controls
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wlts_qgis_dialog import WltsQgisDialog


class WLTSQgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Construct.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WltsQgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&WLTS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('WltsQgis', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = str(Path(Config.BASE_DIR) / 'assets' / 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'wlts'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&WLTS'),
                action)
            self.iface.removeToolBarIcon(action)

    def showHelp(self):
        """Open html doc on default browser."""
        helpfile = (
            Path(os.path.abspath(os.path.dirname(__file__)))
                / 'help' / 'build' / 'html' / 'about.html'
        )
        if os.path.exists(helpfile):
            url = "file://" + str(helpfile)
            self.iface.openURL(url, False)
        else:
            self.basic_controls.alert(
                "error",
                "FileNotFoundError",
                "No help folder found!"
            )
        qgis.utils.showPluginHelp(packageName="wlts_plugin", filename="index", section="about")

    def initIcons(self):
        """Get icons from file system."""
        icon = QIcon(str(Path(Config.BASE_DIR) / 'assets' / 'interrogation-icon.png'))
        self.dlg.show_help_button.setIcon(icon)
        icon = QIcon(str(Path(Config.BASE_DIR) / 'assets' / 'location-icon.png'))
        self.dlg.search_button.setIcon(icon)
        icon = QIcon(str(Path(Config.BASE_DIR) / 'assets' / 'zoom-icon.png'))
        self.dlg.zoom_selected_point.setIcon(icon)
        icon = QIcon(str(Path(Config.BASE_DIR) / 'assets' / 'save-icon.png'))
        self.dlg.export_result.setIcon(icon)
        self.points_layer_icon_path = str(Path(Config.BASE_DIR) / 'assets' / 'marker-icon.png')

    def initControls(self):
        """Init the basic controls to get."""
        self.dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.dlg.setFixedSize(self.dlg.size().width(), self.dlg.size().height())
        self.basic_controls = Controls()
        self.wlts_controls = WLTS_Controls()
        self.files_controls = FilesExport()
        self.enabled_click = True
        self.addCanvasControlPoint(self.enabled_click)
        self.dlg.input_longitude.valueChanged.connect(self.checkFilters)
        self.dlg.input_latitude.valueChanged.connect(self.checkFilters)
        self.getDate()

    def initButtons(self):
        """Init the main buttons to manage services and the results."""
        self.dlg.show_help_button.clicked.connect(self.showHelp)
        self.dlg.export_result.clicked.connect(self.exportAsType)
        self.dlg.search_button.clicked.connect(self.plotTrajectory)
        self.dlg.zoom_selected_point.clicked.connect(self.zoom_to_selected_point)
        self.initExportOptions()
        self.enabledSearchButtons(False)

    def initExportOptions(self):
        """Init the combo box select option to export"""
        self.dlg.export_result_as_type.addItems(self.files_controls.getExportOptions())

    def initHistory(self):
        """Init and update location history."""
        self.dlg.history_list.clear()
        self.selected_location = None
        try:
            self.dlg.history_list.addItems(list(self.locations.keys()))
        except AttributeError:
            self.locations = {}
        self.dlg.history_list.itemClicked.connect(self.getFromHistory)
        self.getLayers()

    def getFromHistory(self, item):
        """Select location from history storage as selected location."""
        self.selected_location = self.locations.get(item.text(), {})
        self.dlg.input_longitude.setValue(self.selected_location.get('long'))
        self.dlg.input_latitude.setValue(self.selected_location.get('lat'))
        self.draw_point(
            self.selected_location.get('long'),
            self.selected_location.get('lat')
        )

    def getLayers(self):
        """Storage the layers in QGIS project."""
        self.layers = QgsProject.instance().layerTreeRoot().children()
        self.layer_names = [layer.name() for layer in self.layers]  # Get all layer names
        self.layer = self.iface.activeLayer()  # QVectorLayer QRasterFile

    def getDate(self):
        """Get the start and end dates of the trajectory."""
        years_interval = 10
        date_string = datetime.today().strftime('%Y-%m-%d')
        end_year = int(date_string[:4]) - years_interval
        self.dlg.start_date.setDate(self.basic_controls.formatForQDate(f"{end_year}-01-01"))
        self.dlg.end_date.setDate(self.basic_controls.formatForQDate(date_string))

    def initCheckBox(self):
        """Start the checkbox with the collections that are active in the service."""
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        collections = self.wlts_controls.listCollections()
        self.checks = {}
        for collection in collections:
            description = self.wlts_controls.description(collection)
            self.checks[collection] = QCheckBox(str(description["title"]))
            self.checks[collection].setChecked(True)
            self.checks[collection].stateChanged.connect(self.checkFilters)
            self.vbox.addWidget(self.checks.get(collection))
        self.widget.setLayout(self.vbox)
        self.dlg.bands_scroll.setWidgetResizable(True)
        self.dlg.bands_scroll.setWidget(self.widget)

    def setCRS(self):
        """Set the CRS in project instance."""
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(int("4326")))

    def getSelected(self):
        """Get the collections that have been selected."""
        self.selected_collections = []
        for key in list(self.checks.keys()):
            if self.checks.get(key).isChecked():
                self.selected_collections.append(key)
        self.start_date = str(self.dlg.start_date.date().toString('yyyy-MM-dd'))
        self.end_date = str(self.dlg.end_date.date().toString('yyyy-MM-dd'))

    def changeDateValue(self, value):
        """Date slider control data on layers QGIS."""
        vector = self.geojson.get("features", [])[value]
        date = vector.get("properties").get("date")
        vlayer = QgsVectorLayer(
            json.dumps(vector),
            (f"Geojson_WLTS_response_{date}"),
            "ogr"
        )
        self.dlg.date_control_slider.setTitle(
            vector.get("properties").get("date") + ", " +
            vector.get("properties").get("collection") + ", " +
            vector.get("properties").get("class")
        )
        self.layers = QgsProject.instance().layerTreeRoot().children()
        for layer in self.layers:
            if "Geojson_WLTS_response_" in layer.name():
                QgsProject.instance().removeMapLayer(layer.layerId())
        QgsProject.instance().addMapLayer(vlayer)

    def exportPython(self):
        """Export as python code."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as python code',
                directory=('wlts_trajectory_download.py'),
                filter='*.py'
            )
            attributes = {
                'host': Config.WLTS_HOST,
                'lat': self.selected_location['lat'],
                'long': self.selected_location['long'],
                'collections': ",".join(self.selected_collections),
                'start': self.start_date,
                'end': self.end_date
            }
            self.files_controls.generateCode(name[0], attributes)
        except AttributeError as error:
            self.basic_controls.alert("warning", "AttributeError", str(error))

    def exportCSV(self):
        """Export to file system trajectory data in CSV."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as CSV',
                directory=('wlts_trajectory_download.csv'),
                filter='*.csv'
            )
            trajectory = self.tj
            self.files_controls.generateCSV(name[0], trajectory)
        except AttributeError as error:
            self.basic_controls.alert("warning", "AttributeError", str(error))

    def exportJSON(self):
        """Export to file system trajectory data in JSON."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as JSON',
                directory=('wlts_trajectory_download.json'),
                filter='*.json'
            )
            self.files_controls.generateJSON(name[0], self.tj)
        except AttributeError as error:
            self.basic_controls.alert("warning", "AttributeError", str(error))

    def plotTrajectory(self):
        """Plot trajectory with files controls."""
        self.getSelected()
        self.tj = self.wlts_controls.getTrajectory(
            lon=float(self.selected_location.get("long")),
            lat=float(self.selected_location.get("lat")),
            collections=self.selected_collections,
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.files_controls.generatePlotFig(self.wlts_controls)

    def plotlyBrowser(self):
        """Redirects user to browser plotly."""
        self.getSelected()
        self.tj = self.wlts_controls.getTrajectory(
            lon=float(self.selected_location.get("long")),
            lat=float(self.selected_location.get("lat")),
            collections=self.selected_collections,
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.files_controls.generatePlotlyFig(self.wlts_controls)

    def exportAsType(self):
        """Export result based on combo box selection."""
        ext = self.dlg.export_result_as_type.currentText()
        if ext == "CSV":
            self.exportCSV()
        elif ext == "JSON":
            self.exportJSON()
        elif ext == "Python":
            self.exportPython()
        elif ext == "Plotly":
            self.plotlyBrowser()

    def remove_layer_by_name(self, layer_name):
        """Remove a layer using name."""
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == layer_name:
                QgsProject.instance().removeMapLayer(layer.id())

    def zoom_to_point(self, longitude, latitude, scale = None):
        """Zoom in to selected location using longitude and latitude."""
        time.sleep(0.30)
        canvas = self.iface.mapCanvas()
        if not scale:
            scale = 200 * (1 / canvas.scale())
        canvas.setExtent(
            QgsRectangle(
                float(longitude) - scale,
                float(latitude) - scale,
                float(longitude) + scale,
                float(latitude) + scale
            )
        )
        canvas.refresh()

    def zoom_to_selected_point(self):
        """Zoom to selected point."""
        self.addCanvasControlPoint(self.enabled_click)
        if (self.dlg.input_longitude.value() != 0 and self.dlg.input_latitude.value() != 0):
            self.dlg.zoom_selected_point.setEnabled(True)
            self.zoom_to_point(
                self.selected_location['long'],
                self.selected_location['lat'],
                scale = 0.1
            )

    def set_draw_point(self, longitude, latitude):
        """Create featur to draw temporary point in canvas."""
        feature = QgsFeature()
        feature.setGeometry(QgsPoint(float(longitude), float(latitude)))
        self.points_layer_data_provider.truncate()
        self.points_layer_data_provider.addFeatures([feature])
        self.points_layer_data_provider.forceReload()

    def draw_point(self, longitude, latitude):
        """Draw the selected points in canvas."""
        self.getLayers()
        if len(self.layers) > 0:
            self.setCRS()
            points_layer_name = "wlts_coordinates_history"
            points_layer_icon_size = 10
            try:
                self.set_draw_point(longitude, latitude)
            except:
                self.remove_layer_by_name(points_layer_name)
                self.points_layer = QgsVectorLayer(
                    "Point?crs=epsg:4326&index=yes",
                    points_layer_name, "memory"
                )
                symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.PointGeometry)
                symbol.deleteSymbolLayer(0)
                symbol.appendSymbolLayer(QgsRasterMarkerSymbolLayer(self.points_layer_icon_path))
                symbol.setSize(points_layer_icon_size)
                self.points_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
                self.points_layer.triggerRepaint()
                QgsProject.instance().addMapLayer(self.points_layer)
                self.points_layer_data_provider = self.points_layer.dataProvider()
                self.set_draw_point(longitude, latitude)

    def save_on_history(self, x, y):
        """Get lng/lat coordinates and save on history list."""
        self.getLayers()
        layer_name = '<none>'
        if self.layer:
            layer_name = str(self.layer.name())
        self.selected_location = {
            'long' : x,
            'lat' : y,
            'layer_name' : layer_name,
            'crs' : 'epsg:4326'
        }
        history_key = str(("[{long:,.7f}, {lat:,.7f}]").format(
            long = self.selected_location.get('long'),
            lat = self.selected_location.get('lat')
        ))
        self.locations[history_key] = self.selected_location
        locations_keys = list(self.locations.keys())
        self.dlg.history_list.clear()
        self.dlg.history_list.addItems(locations_keys)
        self.dlg.history_list.setCurrentRow(len(locations_keys) - 1)

    def display_point(self, pointTool):
        """Get the mouse possition and storage as selected location."""
        x = None
        y = None
        if pointTool == None:
            x = self.dlg.input_longitude.value()
            y = self.dlg.input_latitude.value()
        else:
            x = float(pointTool.x())
            y = float(pointTool.y())
            self.dlg.input_longitude.setValue(x)
            self.dlg.input_latitude.setValue(y)
        try:
            self.save_on_history(x, y)
            self.draw_point(x, y)
        except AttributeError:
            pass

    def addCanvasControlPoint(self, enable):
        """Generate a canvas area to get mouse position."""
        self.point_tool = None
        self.pan_map = None
        self.canvas = self.iface.mapCanvas()
        if enable:
            self.setCRS()
            self.point_tool = QgsMapToolEmitPoint(self.canvas)
            self.point_tool.canvasClicked.connect(self.display_point)
            self.canvas.setMapTool(self.point_tool)
        else:
            self.pan_map = QgsMapToolPan(self.canvas)
            self.canvas.setMapTool(self.pan_map)

    def enableGetLatLng(self):
        """Enable get lat lng to search trajectory data."""
        self.addCanvasControlPoint(True)

    def enabledSearchButtons(self, enable):
        """Enable the buttons to load time series."""
        self.dlg.search_button.setEnabled(enable)
        self.dlg.export_result_as_type.setEnabled(enable)
        self.dlg.export_result.setEnabled(enable)

    def checkFilters(self):
        """Check if lat lng are selected."""
        self.getSelected()
        try:
            if (len(self.selected_collections) > 0 and
                self.dlg.input_longitude.value() != 0 and
                    self.dlg.input_latitude.value() != 0):
                self.enabledSearchButtons(True)
            else:
                self.enabledSearchButtons(False)
        except:
            self.enabledSearchButtons(False)

    def finish_session(self):
        """Methods to finish when dialog close"""
        #
        # Remove mouse click
        self.addCanvasControlPoint(False)
        #
        # Restore sys.path
        if Config.PYTHONPATH_WLTS_PLUGIN:
            try:
                import sys
                sys.path = os.environ['PYTHONPATH_WLTS_PLUGIN'].split(':')
                os.environ.pop('PYTHONPATH_WLTS_PLUGIN')
            except:
                pass

    def dialogShow(self):
        """Rules to start dialog."""
        wlts_qgis = qgis.utils.plugins.get("wlts_plugin", None)
        if wlts_qgis:
            wlts_qgis.dlg.show()
        else:
            self.dlg.show()

    def run(self):
        """Run method that performs all the real work."""
        self.dlg = WltsQgisDialog()
        try:
            # Init Controls
            self.initControls()
            # Add icons to buttons
            self.initIcons()
            # Add functions to buttons
            self.initButtons()
            # History
            self.initHistory()
            # Get collections
            self.initCheckBox()
            # show the dialog
            self.dialogShow()
            # Methods to finish session
            self.dlg.finished.connect(self.finish_session)
        except Exception as e:
            controls = Controls()
            controls.alert("error", "Error while starting plugin!", str(e))
