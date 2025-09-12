# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bdc.team@inpe.br'
__date__ = '2021-08-31'
__copyright__ = 'Copyright 2021, INPE'

import unittest

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from wlts_plugin.wlts_qgis_dialog import WltsQgisDialog


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

