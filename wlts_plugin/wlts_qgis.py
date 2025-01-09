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

import getpass
import json
import os.path
from pathlib import Path

import qgis.utils
from wlts import WLTS
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsProject, QgsVectorLayer
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .controller.config import Config
# Import files exporting controls
from .controller.files_export import FilesExport
# Import the controls for the plugin
from .controller.wlts_qgis_controller import Controls, Services
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wlts_qgis_dialog import WltsQgisDialog


class WltsQgis:
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

    def initControls(self):
        """Init the basic controls to get."""
        self.basic_controls = Controls()
        self.server_controls = Services(user="application")
        self.files_controls = FilesExport()

    def initButtons(self):
        """Init the main buttons to manage services and the results."""
        self.dlg.show_help_button.clicked.connect(self.showHelp)
        self.dlg.save_service.clicked.connect(self.saveService)
        self.dlg.delete_service.clicked.connect(self.deleteService)
        self.dlg.edit_service.clicked.connect(self.editService)
        self.dlg.export_as_python.clicked.connect(self.exportPython)
        self.dlg.export_as_csv.clicked.connect(self.exportCSV)
        self.dlg.export_as_json.clicked.connect(self.exportJSON)
        self.dlg.search.clicked.connect(self.enableGetLatLng)
        self.dlg.date_control_slider.setVisible(False)

    def initHistory(self):
        """Init and update location history."""
        self.dlg.history_list.clear()
        self.selected_location = None
        try:
            self.dlg.history_list.addItems(list(self.locations.keys()))
        except AttributeError:
            self.locations = {}
        self.dlg.history_list.itemActivated.connect(self.getFromHistory)
        self.getLayers()

    def getFromHistory(self, item):
        """Select location from history storage as selected location."""
        self.selected_location = self.locations.get(item.text(), {})

    def getLayers(self):
        """Storage the layers in QGIS project."""
        self.layers = QgsProject.instance().layerTreeRoot().children()
        self.layer_names = [layer.name() for layer in self.layers]  # Get all layer names
        self.layer = self.iface.activeLayer()  # QVectorLayer QRasterFile

    def getDate(self):
        """Get the start and end dates of the trajectory."""
        self.dlg.start_date.setDate(self.basic_controls.formatForQDate("1999-01-01"))
        self.dlg.end_date.setDate(self.basic_controls.formatForQDate("2021-01-01"))

    def initServices(self):
        """Load the registered services based on JSON file."""
        service_names = self.server_controls.getServiceNames()
        if not service_names:
            self.basic_controls.alert("error","502 Error", "The main services are not available!")
        self.dlg.service_selection.addItems(service_names)
        self.dlg.service_selection.activated.connect(self.initCheckBox)
        self.data = self.server_controls.loadServices()
        self.model = QStandardItemModel()
        self.basic_controls.addItemsTreeView(self.model, self.data)
        self.dlg.data.setModel(self.model)
        self.dlg.data.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dlg.data.clicked.connect(self.updateDescription)
        self.updateDescription()

    def saveService(self):
        """Save the service based on name and host input."""
        name_to_save = str(self.dlg.service_name.text())
        host_to_save = str(self.dlg.service_host.text())
        try:
            response = self.server_controls.editService(name_to_save, host_to_save)
            if response != None:
                self.selected_service = host_to_save
                self.dlg.service_name.clear()
                self.dlg.service_host.clear()
                self.updateServicesList()
            else:
                self.basic_controls.alert(
                    "error",
                    "(ValueError, AttributeError)",
                    "It is not a valid WLTS Server!"
                )
        except (ValueError, AttributeError, ConnectionRefusedError) as error:
            self.basic_controls.alert("error", "(ValueError, AttributeError)", str(error))

    def deleteService(self):
        """Delete the selected active service."""
        try:
            host_to_delete = host_to_delete = self.server_controls.findServiceByName(self.metadata_selected.text())
            if host_to_delete == None:
                host_to_delete = self.server_controls.findServiceByName(self.metadata_selected.parent().text())
            self.server_controls.deleteService(host_to_delete.name)
            self.updateServicesList()
        except (ValueError, AttributeError) as error:
            self.basic_controls.alert("error", "(ValueError, AttributeError)", str(error))

    def editService(self):
        """Edit the selected service."""
        try:
            host_to_delete = host_to_delete = self.server_controls.findServiceByName(self.metadata_selected.text())
            if host_to_delete == None:
                host_to_delete = self.server_controls.findServiceByName(self.metadata_selected.parent().text())
            self.dlg.service_name.setText(host_to_delete.name)
            self.dlg.service_host.setText(host_to_delete.host)
        except (ValueError, AttributeError) as error:
            self.basic_controls.alert("error", "(ValueError, AttributeError)", str(error))

    def updateServicesList(self):
        """Update the service list when occurs some change in JSON file."""
        self.data = self.server_controls.loadServices()
        self.model = QStandardItemModel()
        self.basic_controls.addItemsTreeView(self.model, self.data)
        self.dlg.data.setModel(self.model)
        self.dlg.service_selection.clear()
        self.dlg.service_selection.addItems(self.server_controls.getServiceNames())
        self.dlg.service_selection.activated.connect(self.initCheckBox)

    def initCheckBox(self):
        """Start the checkbox with the collections that are active in the service."""
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        collections = self.server_controls.listCollections(
            str(self.dlg.service_selection.currentText())
        )
        self.checks = {}
        for collection in collections:
            self.checks[collection] = QCheckBox(str(collection))
            self.vbox.addWidget(self.checks.get(collection))
        self.widget.setLayout(self.vbox)
        self.dlg.bands_scroll.setWidgetResizable(True)
        self.dlg.bands_scroll.setWidget(self.widget)

    def getSelected(self):
        """Get the collections that have been selected."""
        self.selected_collections = []
        for key in list(self.checks.keys()):
            if self.checks.get(key).isChecked():
                self.selected_collections.append(key)
        self.start_date = str(self.dlg.start_date.date().toString('yyyy-MM-dd'))
        self.end_date = str(self.dlg.end_date.date().toString('yyyy-MM-dd'))

    def getTrajectory(self):
        """Get the trajectory from the filters that were selected."""
        self.selected_service = self.server_controls.findServiceByName(self.dlg.service_selection.currentText()).host
        if self.server_controls.testServiceConnection(self.selected_service):
            try:
                client_wlts = WLTS(url=self.selected_service)
                self.tj = client_wlts.tj(
                    latitude=self.transformSelectedLocation().get('lat', 0),
                    longitude=self.transformSelectedLocation().get('long', 0),
                    geometry=self.dlg.geometries.isChecked(),
                    collections=",".join(
                        self.selected_collections
                    ),
                    start_date=self.start_date,
                    end_date=self.end_date
                )
            except:
                self.basic_controls.alert("warning", "AttributeError", "Please insert a valid token!")

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

    def getGeometries(self):
        """Get geometries from WLTS to add map layer on QGIS."""
        self.dlg.date_control_slider.setVisible(False)
        if self.dlg.geometries.isChecked():
            result = self.tj.get('result', []).get('trajectory', [])
            self.geojson = {
                "type": "FeatureCollection",
                "features": []
            }
            dates = []
            for trajectory in result:
                dates.append(trajectory.get('date', "no-data"))
                self.geojson["features"].append({
                    "type": "Feature",
                    "geometry": trajectory.get('geom', {}),
                    "properties": {
                        "class": trajectory.get('class', "no-data"),
                        "collection": trajectory.get('collection', "no-data"),
                        "date": trajectory.get('date', "no-data")
                    }
                })
            self.changeDateValue(0)
            self.dlg.date_control_slider.setVisible(True)
            self.dlg.date_slider.setMaximum(len(dates) - 1)
            self.dlg.date_slider.valueChanged[int].connect(self.changeDateValue)

    def exportPython(self):
        """Export as python code."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as python code',
                directory=('wlts.{collection}.py').format(
                    collection=str(".".join(self.selected_collections))
                ),
                filter='*.py'
            )
            attributes = {
                'host': self.selected_service,
                'lat': self.selected_location['lat'],
                'long': self.selected_location['long'],
                'collections': ",".join(self.selected_collections),
                'geometry': self.dlg.geometries.isChecked(),
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
                directory=('wlts.{collection}.csv').format(
                    collection=str(".".join(self.selected_collections))
                ),
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
                directory=('wlts.{collection}.json').format(
                    collection=str(".".join(self.selected_collections))
                ),
                filter='*.json'
            )
            self.files_controls.generateJSON(name[0], self.tj)
        except AttributeError as error:
            self.basic_controls.alert("warning", "AttributeError", str(error))

    def plotTrajectory(self):
        """Plot trajectory with files controls."""
        self.files_controls.generatePlotFig(self.tj)

    def displayPoint(self, pointTool):
        """Get the mouse possition and storage as selected location."""
        try:
            try:
                crs = str(self.layer.crs().authid())
            except RuntimeError:
                crs = "Unknown"
            self.selected_location = {
                'layer_name' : str(self.layer.name()),
                'lat' : float(pointTool.y()),
                'long' : float(pointTool.x()),
                'crs' : crs
            }
            history_key = str(
                (
                    "({lat:,.4f},{long:,.4f}) {crs}"
                ).format(
                    crs = crs,
                    lat = self.selected_location.get('lat'),
                    long = self.selected_location.get('long')
                )
            )
            self.locations[history_key] = self.selected_location
            self.dlg.history_list.clear()
            self.dlg.history_list.addItems(list(self.locations.keys()))
            self.dlg.history_list.itemActivated.connect(self.getFromHistory)
            self.getSelected()
            self.getTrajectory()
            self.getGeometries()
            self.plotTrajectory()
        except AttributeError:
            pass

    def addCanvasControlPoint(self, enable):
        """Generate a canvas area to get mouse position."""
        self.enabled_click = False
        self.point_tool = None
        self.displayPoint(self.point_tool)
        if enable:
            self.canvas = self.iface.mapCanvas()
            self.point_tool = QgsMapToolEmitPoint(self.canvas)
            self.point_tool.canvasClicked.connect(self.displayPoint)
            self.canvas.setMapTool(self.point_tool)
            self.displayPoint(self.point_tool)
            self.enabled_click = True

    def transformSelectedLocation(self):
        """Use basic controls to transform any selected projection to EPSG:4326."""
        transformed = self.selected_location
        if self.selected_location.get("crs"):
            transformed = self.basic_controls.transformProjection(
                self.selected_location.get("crs"),
                self.selected_location.get("lat"),
                self.selected_location.get("long")
            )
        return transformed

    def enableGetLatLng(self):
        """Enable get lat lng to search trajectory data."""
        self.addCanvasControlPoint(True)

    def updateDescription(self):
        """Update description."""
        try:
            index = self.dlg.data.selectedIndexes()[0]
            self.metadata_selected = index.model().itemFromIndex(index)
            description = (
                "{service_metadata}\n\n{collection_metadata}".format(
                    service_metadata=self.basic_controls.getDescription(
                        name=str(self.metadata_selected.parent().text()),
                        host=str(self.server_controls.findServiceByName(
                            self.metadata_selected.parent().text()
                        ).host),
                        collections=self.metadata_selected.text()
                    ),
                    collection_metadata=self.basic_controls.getCollectionDescription(
                        self.server_controls,
                        str(self.metadata_selected.parent().text()),
                        self.metadata_selected.text()
                    )
                )
            )
            self.basic_controls.alert("info", "Service Metadata", description)
        except:
            pass

    def run(self):
        """Run method that performs all the real work."""
        self.dlg = WltsQgisDialog()
        self.initControls()
        self.addCanvasControlPoint(True)
        self.initServices()
        self.initIcons()
        self.initButtons()
        self.initHistory()
        self.getDate()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
