"""
Testing suite for the align module
"""

import unittest
from util import get_path
from AmpScan import align


class TestAlign(unittest.TestCase):
    DELTA = 0.01

    def setUp(self):
        """Runs before each unit test.
        Sets up AmpObject object using "stl_file_4.stl" "stl_file_5.stl".
        """
        from AmpScan.core import AmpObject
        # Load 2 spheres with radius 1, and 1.2
        stl_path = get_path("stl_file_5.stl") # R=1
        self.amp1 = AmpObject(stl_path)
        stl_path = get_path("stl_file_4.stl") # R=1.2
        self.amp2 = AmpObject(stl_path)

    def test_align(self):
        """Test that objects that are already centered on origin are aligned correctly"""
        al = align(self.amp1, self.amp2).m

        # Both objects are already centered, so should be close to origin (allowing for some inaccuracy)
        self.assertAlmostEqual(al.vert.mean(axis=0)[0], 0, delta=TestAlign.DELTA)
        self.assertAlmostEqual(al.vert.mean(axis=0)[1], 0, delta=TestAlign.DELTA)
        self.assertAlmostEqual(al.vert.mean(axis=0)[2], 0, delta=TestAlign.DELTA)
