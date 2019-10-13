"""
Testing suite for the registration module
"""

import unittest
from util import get_path
from ampscan import registration, analyse
import math


class TestRegistration(unittest.TestCase):
    DELTA = 0.2

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from ampscan.core import AmpObject

        # Radius = 1
        stl_path = get_path("stl_file_4.stl")
        self.amp1 = AmpObject(stl_path)

        # Radius = 1.2
        stl_path = get_path("stl_file_5.stl")
        self.amp2 = AmpObject(stl_path)

        # Spheroid with major radius 1 and minor 0.5
        stl_path = get_path("stl_file_7.stl")
        self.amp3 = AmpObject(stl_path)

    def test_registration_spheres(self):
        """Test that registration runs on two spheres correctly by checking volume of resultant registered AmpObject.
        Note that this is reliant on an accurate analyse module."""
        reg = registration(self.amp1, self.amp2).reg
        poly = analyse.create_slices(reg, [0.001, 0.999], 0.001, typ='norm_intervals', axis=2)

        # Check the volume is correct
        # Object is a sphere, so area is (4/3)*math.pi*(R**3)
        # In this case R = 1.2
        self.assertAlmostEqual(analyse.est_volume(poly), (4/3)*math.pi*(1.2**3), delta=TestRegistration.DELTA)

        # Test the diameter is correct
        diameter = reg.vert[:, 2].max() - reg.vert[:, 2].min()
        self.assertAlmostEqual(diameter, 1.2*2, delta=TestRegistration.DELTA)

    def test_registration_spheres(self):
        """Test that registration runs between a sphere and a spheroid correctly
        by checking volume of resultant registered AmpObject.
        Note that this is reliant on an accurate analyse module."""
        reg = registration(self.amp3, self.amp1).reg
        poly = analyse.create_slices(reg, [0.001, 0.999], 0.001, typ='norm_intervals', axis=2)

        # Check the volume is correct
        # Object is a sphere, so area is (4/3)*math.pi*(R**3)
        # In this case R = 1
        self.assertAlmostEqual(analyse.est_volume(poly), (4/3)*math.pi*(1**3), delta=TestRegistration.DELTA)

        # Test the diameter is correct
        diameter = reg.vert[:, 2].max() - reg.vert[:, 2].min()
        self.assertAlmostEqual(diameter, 2, delta=TestRegistration.DELTA)

