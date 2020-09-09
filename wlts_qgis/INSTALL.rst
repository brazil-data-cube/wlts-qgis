..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2020 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

Installation
============

The Python QGIS Plugin for WTSS depends essentially on:

- `QGIS version +3 <https://qgis.org/en/site/>`_
- `QT Creator version +5 <https://www.qt.io/download>`_
- `Python version +3 <https://www.python.org/>`_

Development installation
------------------------

Clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/brazil-data-cube/wlts-qgis.git


Go to the source code folder:

.. code-block:: shell

        $ cd wlts-qgis/wlts_qgis

Deploy:

.. code-block:: shell

    $ pb_tool deploy --plugin_path /home/{USER}/.local/share/QGIS/QGIS3/profiles/default/python/plugins

.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python +3::

        python3 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and install requirements::

        pip install --upgrade pip

        pip install pyqt5-tools

        pip install pb-tool