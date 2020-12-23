..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2020 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.


==================================================
Python QGIS Plugin for Web Land Trajectory Service
==================================================

.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/wlts-qgis/blob/master/LICENSE
        :alt: Software License

.. image:: https://img.shields.io/badge/lifecycle-experimental-orange.svg
        :target: https://www.tidyverse.org/lifecycle/#experimental
        :alt: Software Life Cycle

.. image:: https://readthedocs.org/projects/wlts_qgis/badge/?version=latest
        :target: https://wlts_qgis.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord


About
=====

This is an implementation of the `Web Land Trajectory Service specification <https://github.com/brazil-data-cube/wlts-spec>`_.


**W**\ eb **L**\ and **T**\ rajectory **S**\ ervice (WLTS)  is a service that aims to facilitate the access to these various "land use and cover" data collections through a tailored API. The result is tool that allows researchers and specialists to spend their time in the analytical process, once the API provides the integration of these datasets and brings the concept of Land Use and Cover Trajectories as a high level abstraction. The WLTS approach is to use a data model that defines a minimum set of temporal and spatial information to represent different sources and types of data. WLTS can be used in a range of application, such as in validation of land cover data sets, in the selection of trainning samples to support Machine Learning algorithms used in the generation of new classification maps.





For more information on WLTS, see:

- `wlts.py <https://github.com/brazil-data-cube/wlts.py>`_: it is a Python client library that supports the communication to a WTSS service.

- `WLTS Specification <https://github.com/brazil-data-cube/wlts-spec>`_: the WLTS specification using `OpenAPI 3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md>`_ notation.

Installation
============

See `INSTALL.rst <./INSTALL.rst>`_.


License
=======

.. admonition::
    Copyright (C) 2020 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.