"""
Testing suite for the smoothing module
"""

import unittest
from util import get_path
from ampscan import analyse
import math


class TestSmoothing(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies
    DELTA = 0.5

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from ampscan.core import AmpObject
        stl_path = get_path("stl_file_2.stl")
        self.amp = AmpObject(stl_path)
        self.amp2 = AmpObject(stl_path)

    def test_smoothing_nans(self):
        """Tests that NaNs are properly dealt with by smooth method"""
        # Test that smoothing runs
        self.amp.smoothValues()
        # TODO add test with NaNs

    def test_smoothing_volume(self):
        """Tests that smoothing affects the volume within given acceptable range"""
        # TODO check this is actually working properly
        poly1 = analyse.create_slices(self.amp, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        print(analyse.est_volume(poly1))
        
        self.amp.lp_smooth(20)
        poly2 = analyse.create_slices(self.amp, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        print(analyse.est_volume(poly2))
        # self.assertAlmostEqual(analyse.est_volume(poly1), analyse.est_volume(poly2), delta=TestSmoothing.DELTA)
        
        self.amp2.hc_smooth(20)
        poly3 = analyse.create_slices(self.amp2, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        print(analyse.est_volume(poly3))
        # self.assertAlmostEqual(analyse.est_volume(poly1), analyse.est_volume(poly3), delta=TestSmoothing.DELTA)
        self.assertLess(analyse.est_volume(poly1)-analyse.est_volume(poly3), analyse.est_volume(poly1)-analyse.est_volume(poly2))

