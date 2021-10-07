..
    This file is part of Python QGIS Plugin for Web Land Trajectory Service.
    Copyright (C) 2021 INPE.

    Python QGIS Plugin for Web Land Trajectory Service is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

============
Installation
============

The Python QGIS Plugin for WLTS depends essentially on:

- `QGIS version +3 <https://qgis.org/en/site/>`_
- `QT Creator version +5 <https://www.qt.io/download>`_
- `Python version +3 <https://www.python.org/>`_
- `Plugin Builder Tool +3 <http://g-sherman.github.io/plugin_build_tool/>`_

Development Installation - GitHub
---------------------------------

Use ``git`` to clone the software repository:

.. code-block:: shell

    git clone https://github.com/brazil-data-cube/wlts-qgis.git


Go to the source code folder:

.. code-block:: shell

    cd wlts-qgis

Install requirements `pb_tool <https://pypi.org/project/pb-tool/>`_ to deploy and publish QGIS Python plugin and `pytest <https://pypi.org/project/pytest/>`_ to run unit test with WLTS plugin.

.. code-block:: shell

    pip install -e .[all]


Linux
*****

Use ``pb_tool`` to compile and deploy the plugin in Linux OS:

.. code-block:: shell

    cd wlts_plugin
    pb_tool deploy \
        --plugin_path /home/${USER}/.local/share/QGIS/QGIS3/profiles/default/python/plugins


Windows
*******

To deploy the plugin in Windows OS add Python and QGIS Python Scripts to the **PATH** environmental variable such as:

.. code-block:: text

    C:\OSGeo4W\apps\Python39
    C:\OSGeo4W\apps\Python39\Scripts

Now you can work from the command line.

On prompt use ``pb_tool`` to compile and deploy WLTS-QGIS plugin in ``wlts-qgis`` directory:

.. code-block:: text

   pb_tool deploy --plugin_path C:\Users\user\AppData\Roaming\QGIS\QGIS{version}\profiles\default\python\plugins

.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    **1.** Create a new virtual environment linked to Python +3::

        python3 -m venv venv

    **2.** Activate the new environment::

        source venv/bin/activate

    **3.** Update pip and install requirements::

        pip install --upgrade pip
        pip install -e .[all]

    Or you can use Python Anaconda Environment:

    **1.** Create an virtual environment using conda with Python Interpreter Version +3::

        conda create --name wlts-qgis python=3

    **2.** Activate environment::

        conda activate wlts-qgis

    **3.** Update pip and install requirements::

        pip install --upgrade pip
        pip install -e .[all]

Docker Environment Installation
-------------------------------

If is the case of some conflicts or problems on installation with any dependency for plugin, we suggest the docker installation using `Dockerfile`.

Clone the repository with `Dockerfile` and build the docker image with the following command:

.. code-block:: text

    docker build -t wlts_qgis:latest .

Create a directory on your user home.

.. code-block:: text

    mkdir /home/${USER}/geodata/

Enable the host to display connection:

.. code-block:: text

    xhost +

Run a container with the built image.

.. code-block:: text

    docker run --rm -it \
        --name wlts_qgis \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v /home/${USER}/geodata/:/geodata \
        -e DISPLAY=unix$DISPLAY wlts_qgis:latest qgis

This command will start the QGIS software and you can add or create your QGIS projects using the volume directory `/home/${USER}/geodata/`.

Enable WLTS-QGIS Plugin
-----------------------

Run QGIS and open the Plugin Manager (`Manage and install plugins`) and enable the WLTS-QGIS.
