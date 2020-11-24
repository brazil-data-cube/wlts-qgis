# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WltsQgis
                                 A QGIS plugin
 Web Land Trajectory Service
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-31
        git sha              : $Format:%H$
        copyright            : (C) 2020 by INPE
        email                : brazildatacube@inpe.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject
from qgis.gui import QgsMapToolEmitPoint

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wlts_qgis_dialog import WltsQgisDialog
import os.path

import wlts
import csv

# plot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from datetime import datetime, date


class WltsQgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

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

        icon_path = ':/plugins/wlts_qgis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'wlts'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&WLTS'),
                action)
            self.iface.removeToolBarIcon(action)

    def initButtons(self):
        """Init the main buttons to manage services and the results"""
        self.dlg.save_service.clicked.connect(self.saveService)
        self.dlg.delete_service.clicked.connect(self.deleteService)
        self.dlg.edit_service.clicked.connect(self.editService)
        self.dlg.export_as_python.clicked.connect(self.exportPython)
        self.dlg.export_as_csv.clicked.connect(self.exportCSV)
        self.dlg.export_as_json.clicked.connect(self.exportJSON)

    def initServices(self):
        self.service = wlts.WLTS('http://brazildatacube.dpi.inpe.br/dev/wlts')
        self.dlg.service_selection.addItem("WLTS - Brazil Data Cube", self.service)

    def initCheckBox(self):
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        collections = self.service.collections
        self.checks = {}

        for collection in collections:
            self.checks[collection] = QCheckBox(str(collection))
            self.vbox.addWidget(self.checks.get(collection))

        self.widget.setLayout(self.vbox)
        self.dlg.bands_scroll.setWidgetResizable(True)
        self.dlg.bands_scroll.setWidget(self.widget)

    def getSelected(self):
        self.selected_collections = []

        for key in list(self.checks.keys()):

            if self.checks.get(key).isChecked():
                self.selected_collections.append(key)

        self.start_date=str(self.dlg.start_date.date().toString('yyyy-MM-dd'))
        self.end_date=str(self.dlg.end_date.date().toString('yyyy-MM-dd'))

        print(self.selected_collections)
        print("Start date: " + str(self.dlg.start_date.date().toString('yyyy-MM-dd')))
        print("End date: " + str(self.dlg.end_date.date().toString('yyyy-MM-dd')))


    def getTrajectory(self):
        self.tj = self.service.tj(latitude=self.selected_location.get('lat'), 
            longitude=self.selected_location.get('long'), 
            collections=",".join(self.selected_collections),
            start_date=self.start_date, 
            end_date=self.end_date)

        
        print(self.tj)

    def getDate(self):
        self.dlg.start_date.setDate(QDate(1999,1,1))
        self.dlg.end_date.setDate(QDate(2020,1,1))

    def displayPoint(self, pointTool):
        """Get the mouse possition and storage as selected location"""
        try:
            print(float(pointTool.x()), float(pointTool.y()))
            self.selected_location = {
                'lat' : float(pointTool.y()),
                'long' : float(pointTool.x())
            }
            self.getTrajectory()
            self.plot()
            
        except AttributeError:
            pass
        

    def addCanvasControlPoint(self):
        """Generate a canvas area to get mouse position"""
        self.canvas = self.iface.mapCanvas()
        self.point_tool = QgsMapToolEmitPoint(self.canvas)
        self.point_tool.canvasClicked.connect(self.displayPoint)
        self.canvas.setMapTool(self.point_tool)
        self.displayPoint(self.point_tool)

    def exportCSV(self):
        """Export to file system times series data in CSV"""
        try:
            name = QFileDialog.getSaveFileName(
                parent=self.dlg,
                caption='Save as CSV',
                directory=('{collection}.csv').format(
                    collection=str(self.selected_collections),
                ),
                filter='*.csv'
            )
            trajectory = self.tj
            self.generateCSV(name[0], trajectory)
        except AttributeError as error:
            print('Error')

    def plot(self):

        try:
            plt.clf()
            plt.cla()
            plt.close()

            fig = plt.figure(figsize=(8,5))

            df_trajectory =  self.tj.df()
            ax2 = fig.add_subplot()
            font_size=18
            bbox=[0, 0, 1, 1]
            ax2.axis('off')
            mpl_table = ax2.table(cellText = df_trajectory.values, rowLabels = df_trajectory.index, bbox=bbox, colLabels=df_trajectory.columns)
            mpl_table.auto_set_font_size(True)
            mpl_table.set_fontsize(font_size)
            plt.show()
        except:
            print("Sem informações.")
        
    def generateCSV(self, file_name, trajectory):
        try:
            df = trajectory.df()
            df.to_csv(file_name, sep=';', index = False, header=True)
        except FileNotFoundError:
            pass

    def run(self):
        """Run method that performs all the real work"""
        # Init Application
        self.dlg = WltsQgisDialog()
        # self.init_wlts()
        self.addCanvasControlPoint()
        self.initServices()
        self.initCheckBox()
        self.dlg.search.clicked.connect(self.getSelected)
        self.dlg.export_as_csv.clicked.connect(self.exportCSV)
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
