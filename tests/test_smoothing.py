"""
Testing suite for the smoothing module
"""

import unittest
from util import get_path


class TestSmoothing(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from AmpScan.core import AmpObject
        stl_path = get_path("stl_file.stl")
        self.amp = AmpObject(stl_path)

    def test_smoothing(self):
        # Test that smoothing runs
        self.amp.smoothValues()

