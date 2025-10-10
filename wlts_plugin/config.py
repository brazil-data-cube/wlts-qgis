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

import os


class Config:
    """Base configuration for global variables.

    :attribute BASE_DIR(str): Returns app root path.
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    WLTS_HOST = os.getenv("WLTS_HOST", "https://data.inpe.br/bdc/wlts/v1/")

    LCCS_HOST = os.getenv("LCCS_HOST", "https://data.inpe.br/bdc/lccs/v1/")

    PYTHONPATH_WLTS_PLUGIN = os.getenv("PYTHONPATH_WLTS_PLUGIN", None)
