# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'brazildatacube@inpe.br'
__date__ = '2020-08-31'
__copyright__ = 'Copyright 2020, INPE'

import unittest

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from wlts_plugin.wlts_qgis_dialog import WltsQgisDialog

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class WltsQgisDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = WltsQgisDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

if __name__ == "__main__":
    suite = unittest.makeSuite(WltsQgisDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

