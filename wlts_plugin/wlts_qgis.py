"""
WLTS QGIS Plugin.

Python QGIS Plugin for Web Land Trajectory Service.
Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/.
                              -------------------
begin                : 2019-05-04
git sha              : $Format:%H$
copyright            : (C) 2020 by INPE
email                : brazildatacube@dpi.inpe.br

This program is free software.

Python QGIS Plugin for Web Land Trajectory Service.
You can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
Copyright (C) 2019-2021 INPE.
"""


import csv
import json
import os.path
from datetime import date, datetime
from json import loads as json_loads
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wlts
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsProject
from qgis.gui import QgsMapToolEmitPoint

from .files_examples.wlts_controller import Controls, Services
from .resources import *
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
        icon_path = ':/plugins/wlts_plugin/icon.png'
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

    def initControls(self):
        """Init the basic controls to get."""
        self.basic_controls = Controls()
        self.server_controls = Services(user="application")

    def initButtons(self):
        """Init the main buttons to manage services and the results."""
        self.dlg.save_service.clicked.connect(self.saveService)
        self.dlg.delete_service.clicked.connect(self.deleteService)
        self.dlg.edit_service.clicked.connect(self.editService)
        self.dlg.export_as_python.clicked.connect(self.exportPython)
        self.dlg.export_as_csv.clicked.connect(self.exportCSV)
        self.dlg.export_as_json.clicked.connect(self.exportJSON)
        self.dlg.search.clicked.connect(self.getSelected)

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
        self.addCanvasControlPoint()

    def getFromHistory(self, item):
        """Select location from history storage as selected location."""
        self.selected_location = self.locations.get(item.text(), {})

    def getLayers(self):
        """Storage the layers in QGIS project."""
        self.layers = QgsProject.instance().layerTreeRoot().children()
        self.layer_names = [layer.name()
                            for layer in self.layers]  # Get all layer names
        self.layer = self.iface.activeLayer()  # QVectorLayer QRasterFile

    def saveService(self):
        """Save the service based on name and host input."""
        name_to_save = str(self.dlg.service_name.text())
        host_to_save = str(self.dlg.service_host.text())
        try:
            self.server_controls.editService(name_to_save, host_to_save)
            self.selected_service = host_to_save
            self.dlg.service_name.clear()
            self.dlg.service_host.clear()
            self.updateServicesList()
        except (ValueError, AttributeError, ConnectionRefusedError) as error:
            self.basic_controls.alert(
                "(ValueError, AttributeError)", str(error))

    def deleteService(self):
        """Delete the selected active service."""
        host_to_delete = self.dlg.service_selection.currentText()
        try:
            self.server_controls.deleteService(host_to_delete)
            self.updateServicesList()
        except (ValueError, AttributeError) as error:
            self.basic_controls.alert(
                "(ValueError, AttributeError)", str(error))

    def editService(self):
        """Edit the selected service."""
        self.dlg.service_name.setText(self.dlg.service_selection.currentText())
        self.dlg.service_host.setText(
            self.server_controls.findServiceByName(
                self.dlg.service_selection.currentText()).host
        )

    def updateServicesList(self):
        """Update the service list when occurs some change in JSON file."""
        self.data = self.server_controls.loadServices()
        self.model = QStandardItemModel()
        self.basic_controls.addItemsTreeView(self.model, self.data)
        self.dlg.data.setModel(self.model)
        self.dlg.service_selection.clear()
        self.dlg.service_selection.addItems(
            self.server_controls.getServiceNames())
        self.dlg.service_selection.activated.connect(self.initCheckBox)

    def initServices(self):
        """Load the registered services based on JSON file."""
        service_names = self.server_controls.getServiceNames()
        if not service_names:
            self.basic_controls.alert("502 Error", "The main services are not available!")
        self.dlg.service_selection.addItems(service_names)
        self.dlg.service_selection.activated.connect(self.selected_service)
        self.data = self.server_controls.loadServices()
        self.model = QStandardItemModel()
        self.basic_controls.addItemsTreeView(self.model, self.data)
        self.dlg.data.setModel(self.model)
        self.dlg.data.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dlg.data.clicked.connect(self.updateDescription)
        self.updateDescription()

    def updateDescription(self):
        """Update description."""
        try:
            index = self.dlg.data.selectedIndexes()[0]
            self.metadata_selected = index.model().itemFromIndex(index)
            widget = QWidget()
            vbox = QVBoxLayout()
            label = QLabel(
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
            label.setWordWrap(True)
            label.heightForWidth(180)
            vbox.addWidget(label)
            widget.setLayout(vbox)
            self.dlg.metadata_scroll.setWidgetResizable(True)
            self.dlg.metadata_scroll.setWidget(widget)
        except:
            widget = QWidget()
            vbox = QVBoxLayout()
            label = QLabel("Select a collection!")
            label.setWordWrap(True)
            label.heightForWidth(180)
            vbox.addWidget(label)
            widget.setLayout(vbox)
            self.dlg.metadata_scroll.setWidgetResizable(True)
            self.dlg.metadata_scroll.setWidget(widget)

    def selected_service(self):
        """Select an service."""
        self.server_controls.listCollections(
            str(self.dlg.service_selection.currentText())
        )

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

        self.start_date = str(
            self.dlg.start_date.date().toString('yyyy-MM-dd'))
        self.end_date = str(self.dlg.end_date.date().toString('yyyy-MM-dd'))

    def getTrajectory(self):
        """Get the trajectory from the filters that were selected."""
        service_host = self.server_controls.findServiceByName(self.dlg.service_selection.currentText()).host
        if self.server_controls.testServiceConnection(service_host):
            client_wlts = wlts.WLTS(service_host)
            self.tj = client_wlts.tj(latitude=self.selected_location.get('lat'),
                                    longitude=self.selected_location.get('long'),
                                    collections=",".join(
                                        self.selected_collections),
                                    start_date=self.start_date,
                                    end_date=self.end_date)



    def getDate(self):
        """Get the start and end dates of the trajectory."""
        self.dlg.start_date.setDate(QDate(1999, 1, 1))
        self.dlg.end_date.setDate(QDate(2020, 1, 1))

    def displayPoint(self, pointTool):
        """Get the mouse possition and storage as selected location."""
        try:
            self.selected_location = {
                'lat': float(pointTool.y()),
                'long': float(pointTool.x())
            }

            history_key = str(
                (
                    "({lat:,.2f},{long:,.2f})"
                ).format(
                    lat=self.selected_location.get('lat'),
                    long=self.selected_location.get('long')
                )
            )

            self.locations[history_key] = self.selected_location
            self.dlg.history_list.clear()
            self.dlg.history_list.addItems(list(self.locations.keys()))
            self.dlg.history_list.itemActivated.connect(self.getFromHistory)

            self.getTrajectory()
            self.plot()

        except AttributeError:
            pass

    def addCanvasControlPoint(self):
        """Generate a canvas area to get mouse position."""
        self.canvas = self.iface.mapCanvas()
        self.point_tool = QgsMapToolEmitPoint(self.canvas)
        self.point_tool.canvasClicked.connect(self.displayPoint)
        self.canvas.setMapTool(self.point_tool)
        self.displayPoint(self.point_tool)

    def exportPython(self):
        """Export as python code."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as python code',
                directory=('{collection}.py').format(
                    collection=str(self.selected_collections),
                ),
                filter='*.py'
            )

            attributes = {
                'service_host': self.service._url,
                'latitude': self.selected_location['lat'],
                'longitude': self.selected_location['long'],
                'collections': ",".join(self.selected_collections)
            }
            self.generateCode(name[0], attributes)
        except AttributeError:
            pass

    def generateCode(self, file_name, attributes):
        """Generate python code to export."""
        try:
            file = self.defaultCode()

            code_to_save = file.format(**attributes)
            file_to_save = open(file_name, "w")
            file_to_save.write(code_to_save)
            file_to_save.close()
        except FileNotFoundError:
            pass

    def defaultCode(self):
        """Return a default python code with blank WLTS parameters."""
        template = (
                Path(os.path.abspath(os.path.dirname(__file__)))
                / 'files_examples'
                / 'trajectory_export_template.py'
        )
        return open(template, 'r').read()

    def exportCSV(self):
        """Export to file system trajectory data in CSV."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as CSV',
                directory=('{collections}.csv').format(
                    collections=str(self.selected_collections),
                ),
                filter='*.csv'
            )
            trajectory = self.tj
            self.generateCSV(name[0], trajectory)
        except AttributeError as error:
            self.basic_controls.alert("Error", "error")

    def generateCSV(self, file_name, trajectory):
        """Create the .csv file."""
        try:
            df = trajectory.df()
            dict = {}

            latlng = [self.selected_location.get(
                'lat'), self.selected_location.get('long')]

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

    def exportJSON(self):
        """Export to file system trajectory data in JSON."""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as JSON',
                directory=('{collection}.json').format(
                    collection=str(self.selected_collections),
                ),
                filter='*.json'
            )
            trajectory = self.tj
            with open(name[0], 'w') as outfile:
                json.dump(trajectory, outfile)
        except AttributeError as error:
            self.basic_controls.alert("Error", "error")

    def plot(self):
        """Create a table with the trajectory."""
        try:
            plt.clf()
            plt.cla()
            plt.close()

            fig = plt.figure(figsize=(8, 5))

            df_trajectory = self.tj.df()
            ax2 = fig.add_subplot()
            font_size = 18
            bbox = [0, 0, 1, 1]
            ax2.axis('off')
            mpl_table = ax2.table(cellText=df_trajectory.values,
                                  rowLabels=df_trajectory.index, bbox=bbox, colLabels=df_trajectory.columns)
            mpl_table.auto_set_font_size(True)
            mpl_table.set_fontsize(font_size)
            plt.show()
        except:
            self.basic_controls.alert("Error", "Sem informações")

    def run(self):
        """Run method that performs all the real work."""
        self.dlg = WltsQgisDialog()
        self.initControls()
        self.addCanvasControlPoint()
        self.initServices()
        self.initCheckBox()
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
