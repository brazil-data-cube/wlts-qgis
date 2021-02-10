import json
from json import loads as json_loads
from pathlib import Path
from types import SimpleNamespace

import requests
from pyproj import Proj, transform
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMessageBox
from wlts import WLTS

from .config import BASE_DIR


class Controls:
    """
    Sample controls to main class plugin

    Methods:
        alert
        addItemsTreeView
        formatForQDate
        transformProjection
        getDescription
    """

    def alert(self, title, text):
        """
        Show alert message box with a title and info

        Args:
            title<string>: the message box title
            text<string>: the message box info
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def addItemsTreeView(self, parent, elements):
        """
        Create a data struct based on QGIS Tree View

        Args:
            parent<QStandardItemModel>: the parent node of data struct
            elements<tuple>: list of items in array of tuples
        """
        for text, children in elements:
            item = QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.addItemsTreeView(item, children)

    def formatForQDate(self, date_string):
        """
        Return a QDate format

        Args:
            date_string<string>: date string with 'yyyy-mm-dd' format
        """
        return QDate(
            int(date_string[:4]),
            int(date_string[5:-3]),
            int(date_string[8:])
        )

    def transformProjection(self, projection, latitude, longitude):
        # transform any projection to EPSG: 4326
        """
        Transform any projection to EPSG: 4326

        Args:
            projection<string>: string format 'EPSG: 4326'
            latitude<float>: the point latitude
            longitude<float>: the point longitude
        """
        lat, lon = transform(
            Proj(init=projection),
            Proj(init='epsg:4326'),
            latitude, longitude
        )
        return {
            "lat": lat,
            "long": lon,
            "crs": "EPSG: 4326"
        }

    def getDescription(self, name="Null", host="Null", collections="Null"):
        """
        Returns a service description format string

        Args:
            name<string> optional: service name
            host<string> optional: service host
            collection<string> optional: activate collection
        """
        return (
                "Service name: " + name + "\n" +
                "Host: " + host + "\n" +
                "Active collections: " + collections + "\n"
        )

    def getCollectionDescription(self, server_controls=None, service="", collection=""):
        """
        Get description from WLTS Server and format for show

        Args:
            server_controls<Services>: server controls to set services
            service<string>: the service name save on server controls
            collection<string>: the collection name selected
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


class Service:
    """
    Service class to map json dumps
    """
    def __init__(self, index, name, host):
        self.id = index
        self.name = name
        self.host = host


class ServiceList:
    """
    Service list class to store like json file
    """
    def __init__(self, services):
        self.services = services


class Services:
    """
    Class for the service storage rule

    Args:
        user<string>: users control to storage services in a JSON file

    Methods:
        getPath
        testServiceConnection
        resetAvailableServices
        getServices
        getServiceNames
        loadServices
        findServiceByName
        addService
        deleteService
        editService
    """

    def __init__(self, user):
        try:
            self.user = user
            self.services = self.getServices()
        except FileNotFoundError:
            self.resetAvailableServices()

    def getPath(self):
        """
        Return the location of JSON with registered services
        """
        return (
                Path(BASE_DIR)
                / 'json-schemas'
                / ('services_storage_user_' + self.user + '.json')
        )

    def testServiceConnection(self, host):
        """
        Check if sevice is available testing connection

        Args:
            host<string>: the service host string
        """
        try:
            wlts = WLTS(host)
            wlts.collections
            return True
        except:
            return False

    def resetAvailableServices(self):
        """
        Restart the list of services with default sevices available
        """
        self.addService("Brazil Data Cube", "https://brazildatacube.dpi.inpe.br/dev/wlts")
        if not self.getServiceNames():
            to_save = json_loads(json.dumps(ServiceList([]).__dict__))
            with open(str(self.getPath()), 'w') as outfile:
                json.dump(to_save, outfile)

    def description(self, service_name, collection_name):
        host = self.findServiceByName(service_name).host
        if self.testServiceConnection(host):
            client_wlts = WLTS(host)
            return client_wlts[collection_name]
        else:
            return {}

    def getServices(self):
        """
        Returns a dictionary with registered services
        """
        with self.getPath().open() as f:
            return json.loads(
                f.read(),
                object_hook=lambda d: SimpleNamespace(**d)
            )

    def getServiceNames(self):
        """
        Returns a list of registered service names
        """
        try:
            service_names = []
            for server in self.getServices().services:
                if self.testServiceConnection(server.host):
                    service_names.append(server.name)
            return service_names
        except (FileNotFoundError, FileExistsError):
            return []

    def loadServices(self):
        """
        Returns the services in a data struct based on QGIS Tree View
        """
        try:
            servers = []
            for server in self.getServices().services:
                if self.testServiceConnection(server.host):
                    client_wlts = WLTS(server.host)
                    collection_tree = []
                    for collection in client_wlts.collections:
                        collection_tree.append((collection, []))
                    servers.append((server.name, collection_tree))
                else:
                    self.deleteService(server.name)
            return [('Services', servers)]
        except (FileNotFoundError, FileExistsError):
            return [('Services', servers)]

    def findServiceByName(self, service_name):
        """
        Return the service in a dictionary finding by name
        Args:
            service_name<string>: the service registered name
        """
        try:
            service = None
            for server in self.getServices().services:
                if str(server.name) == str(service_name):
                    service = server
            return service
        except (FileNotFoundError, FileExistsError):
            return None

    def listCollections(self, service_name):
        """
        Return a dictionary with the list of available products
        Args:
            service_name<string>: the service registered name
        """
        host = self.findServiceByName(service_name).host
        if self.testServiceConnection(host):
            client_wlts = WLTS(host)
            return client_wlts.collections
        else:
            return []

    def addService(self, name, host):
        """
        Register an active service

        Args:
            name<string>: the service name to save
            host<string>: the URL service to save
        """
        try:
            server_to_save = self.findServiceByName(name)
            if self.testServiceConnection(host) and server_to_save == None:
                try:
                    to_save = self.getServices()
                    index = to_save.services[len(to_save.services) - 1].id + 1
                except (IndexError, FileNotFoundError, FileExistsError):
                    to_save = ServiceList([])
                    index = 0
                server_to_save = Service(index, str(name), str(host))
                to_save.services.append(server_to_save)
                for i in range(len(to_save.services)):
                    to_save.services[i] = json_loads(
                        json.dumps(to_save.services[i].__dict__)
                    )
                to_save = json_loads(json.dumps(to_save.__dict__))
                with open(str(self.getPath()), 'w') as outfile:
                    json.dump(to_save, outfile)
            return server_to_save
        except (FileNotFoundError, FileExistsError):
            return None

    def deleteService(self, server_name):
        """
        Delete a service finding by name
        Args:
            server_name<string>: the service name to delete
        """
        try:
            server_to_delete = self.findServiceByName(server_name)
            if server_to_delete != None:
                to_delete = self.getServices()
                to_delete.services.pop(
                    to_delete.services.index(server_to_delete)
                )
                for i in range(len(to_delete.services)):
                    to_delete.services[i] = json_loads(json.dumps(to_delete.services[i].__dict__))
                to_delete = json_loads(json.dumps(to_delete.__dict__))
                with open(str(self.getPath()), 'w') as outfile:
                    json.dump(to_delete, outfile)
            return server_to_delete
        except (FileNotFoundError, FileExistsError):
            return None

    def editService(self, server_name, server_host):
        """
        Edit the service data finding by name

        Args:
            name<string>: the service name to find
            host<string>: the URL service to edit
        """
        server_to_edit = self.findServiceByName(server_name)
        if server_to_edit != None:
            self.deleteService(server_name)
        return self.addService(
            server_name,
            server_host
        )