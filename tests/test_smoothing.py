"""
Testing suite for the smoothing module
"""

import unittest
from util import get_path
from ampscan import analyse
import math
import numpy as np


class TestSmoothing(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies
    DELTA = 0.5

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from ampscan.core import AmpObject
        stl_path = get_path("stl_file.stl")
        self.amp = AmpObject(stl_path)
        self.amp2 = AmpObject(stl_path)
        self.amp3 = AmpObject(stl_path)
        self.amp4 = AmpObject(stl_path)

    def test_smoothing_nans(self):
        """Tests that NaNs are properly dealt with by smooth method"""
        # Test that smoothing runs
        self.amp.smoothValues()
        # TODO add test with NaNs

    def test_smoothing_volume(self):
        """Tests that smoothing affects the volume within given acceptable range"""
        # TODO check this is actually working properly
        poly1 = analyse.create_slices(self.amp, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        vol1 = analyse.est_volume(poly1) 
        print(vol1)
        
        self.amp2.lp_smooth(20)
        poly2 = analyse.create_slices(self.amp2, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        vol2 = analyse.est_volume(poly2) 
        print(vol2)
        # self.assertAlmostEqual(analyse.est_volume(poly1), analyse.est_volume(poly2), delta=TestSmoothing.DELTA)
        
        self.amp3.hc_smooth(n=20)
        poly3 = analyse.create_slices(self.amp3, [0.01, 0.99], 0.005, typ='norm_intervals', axis=2)
        vol3 = analyse.est_volume(poly3) 
        print(vol3)
        # self.assertAlmostEqual(analyse.est_volume(poly1), analyse.est_volume(poly3), delta=TestSmoothing.DELTA)
        self.assertLess(vol1-vol3, vol1-vol2)
        
    def test_coincident(self):
        idx_max = np.argmax(self.amp4.vert[:, 1])
        idx_min = np.argmin(self.amp4.vert[:, 1])
        delta = self.amp4.vert[idx_max, 1] - self.amp4.vert[idx_min, 1]
        self.amp4.vert[idx_max, :] = self.amp4.vert[idx_min, :]
        self.amp4.vert[idx_max, :] = self.amp4.vert[idx_min, :]
        self.amp4.adjustCoincident(beta=1)
        delta2 = self.amp4.vert[idx_max, 1] - self.amp4.vert[idx_min, 1]
        self.assertGreater(delta2, delta*0.99)
        
        

