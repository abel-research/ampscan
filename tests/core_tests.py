"""
Testing suite for the core functionality
"""

import unittest
import os
import numpy as np


def suite():
    """
    Build testing suite from unittests in module
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestCore)


class TestCore(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies

    def setUp(self):
        """
        Runs before each unit test
        Sets up the AmpObject object using "sample_stl_sphere_BIN.stl"
        """
        from AmpScan.core import AmpObject
        stl_path = self.get_path("sample_stl_sphere_BIN.stl")
        self.amp = AmpObject(stl_path)

    def test_centre(self):
        """
        Test the centre method of AmpObject
        """

        # Translate the mesh
        self.amp.translate([1, 0, 0])
        # Recenter the mesh
        self.amp.centre()
        centre = self.amp.vert.mean(axis=0)

        # Check that the mesh is centred correctly (to at least the number of decimal places of ACCURACY)
        self.assertTrue(all(centre[i] < (10**-TestCore.ACCURACY) for i in range(3)))

    def test_rotate(self):
        """
        Tests the rotate method of AmpObject
        """

        # Test rotation on first node
        rot = [np.pi/2, -np.pi/4, np.pi/3]
        before_vert_pos = self.amp.vert[0][:]
        self.amp.rotateAng(rot)
        after_vert_pos = self.amp.vert[0][:]
        np.dot(before_vert_pos, rot)
        self.assertAlmostEqual(before_vert_pos, after_vert_pos, TestCore.ACCURACY)

        # Check single floats cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotateAng(7)

        # Check dictionaries cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotateAng(dict())

    def test_translate(self):
        """
        Test translating method of AmpObject
        """

        # Check that everything has been translated correctly to a certain accuracy
        start = self.amp.vert.mean(axis=0)[:]
        self.amp.translate([1, -1, 0])
        end = self.amp.vert.mean(axis=0)[:]
        self.assertAlmostEqual(start[0]+1, end[0], places=TestCore.ACCURACY)
        self.assertAlmostEqual(start[1]-1, end[1], places=TestCore.ACCURACY)
        self.assertAlmostEqual(start[2], end[2], places=TestCore.ACCURACY)

        # Check that translating raises TypeError when translating with an invalid type
        with self.assertRaises(Exception):
            self.amp.translate("")

        # Check that translating raises ValueError when translating with 2 dimensions
        with self.assertRaises(ValueError):
            self.amp.translate([0, 0])

        # Check that translating raises ValueError when translating with 4 dimensions
        with self.assertRaises(ValueError):
            self.amp.translate([0, 0, 0, 0])

    def get_path(self, filename):
        """
        Returns the absolute path to the testing files

        :param filename: Name of the file in tests folder
        :return: The absolute path to the file
        """

        # Check if the parent directory is tests (this is for Pycharm unittests)
        if os.path.basename(os.getcwd()) == "tests":
            # This is for Pycharm testing
            stl_path = filename
        else:
            # This is for the Gitlab testing
            stl_path = os.path.abspath(os.getcwd()) + "\\tests\\"+filename
        return stl_path

