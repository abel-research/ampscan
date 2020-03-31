"""
Testing suite for the registration module
"""

import unittest
from util import get_path
from ampscan import analyse
import math


class TestAnalyse(unittest.TestCase):
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
        """Test the analyse module by calculating the theoretical volume of a sphere 
        and compring """
        # Check the volume is correct
        # Object is a sphere, so area is (4/3)*math.pi*(R**3)
        # In this case R = 1.2
        self.assertAlmostEqual(analyse.calc_volume_closed(self.amp2), (4/3)*math.pi*(1.2**3), delta=TestAnalyse.DELTA)