"""
Testing suite for the smoothing module
"""

import unittest
from util import get_path
from AmpScan import analyse
import math


class TestSmoothing(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies
    DELTA = 0.5

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from AmpScan.core import AmpObject
        stl_path = get_path("stl_file_4.stl")
        self.amp = AmpObject(stl_path)

    def test_smoothing_nans(self):
        # Test that smoothing runs
        self.amp.smoothValues()
        # TODO add test with NaNs

    def test_smoothing_volume(self):
        # TODO check this is actually working properly
        poly1 = list(analyse.create_slices(self.amp, [0.001, 0.999], 0.001, typ='norm_intervals', axis=2))
        self.amp.smoothValues(1)
        poly2 = list(analyse.create_slices(self.amp, [0.001, 0.999], 0.001, typ='norm_intervals', axis=2))
        print(analyse.est_volume(poly1), analyse.est_volume(poly2))
        self.assertAlmostEqual(analyse.est_volume(poly1), analyse.est_volume(poly2), delta=TestSmoothing.DELTA)

