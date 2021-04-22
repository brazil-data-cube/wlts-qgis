..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2021 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

==================================================
Python QGIS Plugin for Web Land Trajectory Service
==================================================

.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/wlts-qgis/blob/master/LICENSE
        :alt: Software License

.. image:: https://drone.dpi.inpe.br/api/badges/brazil-data-cube/wlts-qgis/status.svg
        :target: https://drone.dpi.inpe.br/brazil-data-cube/wlts-qgis
        :alt: Build Status

.. .. image:: https://coveralls.io/repos/github/brazil-data-cube/wlts-qgis/badge.svg?branch=master
        :target: https://coveralls.io/github/brazil-data-cube/wlts-qgis?branch=master
        :alt: Code Coverage Test

.. image:: https://readthedocs.org/projects/wlts-qgis/badge/?version=latest
        :target: https://wlts-qgis.readthedocs.io/en/latest/
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/lifecycle-experimental-orange.svg
        :target: https://www.tidyverse.org/lifecycle/#experimental
        :alt: Software Life Cycle

.. .. image:: https://img.shields.io/github/tag/brazil-data-cube/wlts-qgis.svg
        :target: https://github.com/brazil-data-cube/wlts-qgis/releases
        :alt: Release

.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord


About
=====

Information on land use and land cover is essential to support governments in making decisions about the impact of human activities on the environment, planning the use of natural resources, conserving biodiversity and monitoring climate change.

Currently, several projects systematically provide information on the dynamics of land use and cover. Well known projects include PRODES, DETER and TerraClass. These projects are developed by INPE and they produce information on land use and coverage used by the Brazilian Government to make public policy decisions. Besides these projects there are other initiatives from universities and space agencies devoted to the creation of national and global maps.

Although these projects follow open data policies and provide a rich collection of data, there is still a gap in tools that facilitate the integrated use of these collections. Each project adopts its own land use and land cover classification system, providing different class names and meanings for the elements of these collections. The forms of distribution of project data can be carried out in different ways, through files or web services. In addition, the data has different spatial and temporal resolutions and storage systems (raster or vector).

In this context, the Web Land Trajectory Service (WLTS) is a service that aims to facilitate the access to these vaapproach consists of using a data model that defines a minimum set of temporal and spatial information to represent different sources and types of data, but with a focus on land use and land cover.

WLTS can be used in a variety of applications, such as validating land cover data sets, selecting training samples to support Machine Learning algorithms used in the generation of new classification maps.

WLTS is based on three operations:

- list_collection: returns the list of all available collection in the service.
- describe_collection: returns the metadata of a given collection.
- trajectory:  returns the land use and cover trajectory from the collections given a location in space


For more information on WLTS, see:

- `wlts.py <https://github.com/brazil-data-cube/wlts.py>`_: it is a Python client library that supports the communication to a WLTS service.

- `rwlts <https://github.com/brazil-data-cube/rwlts>`_: it is a R client library that supports the communication to a WLTS service.

- `WLTS Specification <https://github.com/brazil-data-cube/wlts-spec>`_: the WLTS specification using `OpenAPI 3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md>`_ notation.

- `WLTS <https://github.com/brazil-data-cube/wlts>`_: the WLTS service.

The following image presents an overview of the plugin:

.. image:: https://github.com/brazil-data-cube/wlts-qgis/wlts_plugin/help/source/assets/img/wlts-qgis.png
        :target: https://github.com/brazil-data-cube/wlts-qgis/wlts_plugin/help/source/assets/img/
        :width: 70%
        :alt: WLTS-QGIS


Installation
============

See `INSTALL.rst <https://github.com/brazil-data-cube/wlts-qgis/tree/master/wlts_plugin/help/source/install.rst>`_.


Documentation
=============

**Under Development**

.. See https://wlts-qgis.readthedocs.io/en/latest/


License
=======

.. admonition::
    Copyright (C) 2021 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.