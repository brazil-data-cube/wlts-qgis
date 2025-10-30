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

"""Python QGIS Plugin for WLTS."""

from .config import InstallDependencies

installDependencies = InstallDependencies(__file__)

def classFactory(iface):
    """Load wlts_qgis class from file wlts_qgis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    # Setting PYTHONPATH to use dependencies
    installDependencies.set_lib_path()
    try:
        #
        # Test import of dependencies
        from .wlts_qgis import WLTSQgis
    except (ModuleNotFoundError, ImportError) as error:
        #
        # Run packages installation
        installDependencies.run_install_pkgs_process(error_msg=error)
        #
        # Test imports of dependencies again
        from .wlts_qgis import WLTSQgis
    #
    # Start plugin GUI
    return WLTSQgis(iface)
