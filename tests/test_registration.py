"""
Testing suite for the registration module
"""

import unittest
from util import get_path
from AmpScan import registration


class TestRegistration(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from AmpScan.core import AmpObject
        stl_path = get_path("stl_file_4.stl")
        self.amp1 = AmpObject(stl_path)
        stl_path = get_path("stl_file_5.stl")
        self.amp2 = AmpObject(stl_path)

    def test_registration_spheres(self):
        """Test that registration runs on two spheres correctly"""
        reg = registration(self.amp1, self.amp2).reg
        # TODO add test to check that output is correct

