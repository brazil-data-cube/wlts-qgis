..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2021 INPE.

    Python QGIS Plugin for Web Land Trajectory Service. is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

=====
Usage
=====

To use the WLTS extension to retrieve land use and land cover trajectories it is necessary to generate a user access token in `BDC Auth App <https://brazildatacube.dpi.inpe.br/auth-app>`_.

Enable WLTS-QGIS Plugin
+++++++++++++++++++++++

Open QGIS Desktop and add a vector layer as the figure below:

.. image:: ./assets/screenshots/step-one.png
    :width: 100%
    :alt: QGIS Desktop

Go to ``Plugins`` tab in ``Management Plugins`` option to verify if WLTS-QGIS is enable. You will find the follow information such a figure below:

.. image:: ./assets/screenshots/step-two.png
    :width: 100%
    :alt: Enable WLTS-PLUGIN

Run WLTS-QGIS Plugin
++++++++++++++++++++

You can open the WLTS-QGIS Plugin in ``Web`` tab. The following screen will appear:

.. image:: ./assets/screenshots/step-three.png
    :width: 100%
    :alt: WLTS-PLUGIN

You must select a ``WLTS service`` that you want to use. And choose the ``collections`` to retrieve the trajectory information. You can also edit a ``start`` and ``end date``. Finally click on ``SEARCH`` button to enable the mouse event to get a ``latitude`` and ``longitude`` in vector layer with mouse.

After that, a ``land use and cover trajectory`` will be displayed in new screen, such a figure:

.. image:: ./assets/screenshots/step-four.png
    :width: 100%
    :alt: WLTS-PLUGIN
