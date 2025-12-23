..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2025 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


Changes
=======

Version 1.0.0 (2025-12-23)
--------------------------

- Add as default search the collections PRODES and IBGE (#86);
- Add colors on trajectory plot based on classification system of collection using LCCS (#85);

Version 0.8.0 (2025-09-12)
--------------------------

- Update documentation (#81);
- Review source code structure to publish in QGIS plugins web portal (#79);
- Update and remove unused interface to get trajectories (#78);
- Update WLTS client version (#77);
- Resolve coordinates/layers projection in enable canvas points selection (#76);
- Review the method to generate visualization for trajectories (#75);
- Review and update methods for the installation and build steps for plugin (#74);
- Update default service to WLTS from COIDS environment (#73);
- Remove access token dependence and tokens storage controls (#72) opened on Jan 9
- Review dependencies in setup.py and update to pyproject (#71);
- Change license to GPL v3 (#70);
- Add a dialog box with the collection info (#69);
- Enable a list of points in the WLTS request (#57);
- Review how plugin is handling http errors (#55);
- Review how the plugin is handling entry dates for start and end dates (#47);

Version 0.6.0 (2021-04-23)
--------------------------

- Support for the `WLTS specification version 0.6.0 <https://github.com/brazil-data-cube/wlts-spec>`_.

- Adding unit tests to plugin source code.

- Adding Drone integration (`#49 <https://github.com/brazil-data-cube/wlts-qgis/issues/49>`_).

- Adding support for layer projections (`#62 <https://github.com/brazil-data-cube/wlts-qgis/issues/62>`_).

- Adding support for get geometries from WLTS (`#56 <https://github.com/brazil-data-cube/wlts-qgis/issues/56>`_).

- Improve the handling of http errors (`#55 <https://github.com/brazil-data-cube/wlts-qgis/issues/55>`_).

- Improve documentation for installation and usage (`#51 <https://github.com/brazil-data-cube/wlts-qgis/issues/51>`_).


Version 0.4.0-0 (2021-01-13)
----------------------------


- Support for the `WLTS specification version 0.4.0-0 <https://github.com/brazil-data-cube/wlts-spec/tree/b-0.4>`_.

- Documentation system based on Sphinx.

- Installation and build instructions.

- Package support through Setuptools.

- Usage instructions.

- Source code versioning based on `Semantic Versioning 2.0.0 <https://semver.org/>`_.

- License: `MIT <https://github.com/gqueiroz/wlts.py/blob/master/LICENSE>`_.
