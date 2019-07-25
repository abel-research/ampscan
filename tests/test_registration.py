"""
Testing suite for the core module
"""

import unittest
import os
import numpy as np
from random import randrange


class TestCore(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "sample_stl_sphere_BIN.stl".
        """
        from AmpScan.core import AmpObject
        stl_path = self.get_path("sample_stl_sphere_BIN.stl")
        self.amp = AmpObject(stl_path)

