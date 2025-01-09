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

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WltsQgis class from file WltsQgis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .wlts_qgis import WltsQgis
    return WltsQgis(iface)