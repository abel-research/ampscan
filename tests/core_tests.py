# -*- coding: utf-8 -*-
"""
Testing suite for the core functionality
"""

import unittest
import os
import sys


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestCore)


class TestCore(unittest.TestCase):
    ACCURACY = 3  # The number of decimal places to value accuracy for

    def setUp(self):
        """
        Set up the AmpObject object from "sample_stl_sphere_BIN.stl"
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
        s = str(type(self.amp))
        self.assertEqual(s, "<class 'AmpScan.core.AmpObject'>", "Not expected Object")
        with self.assertRaises(TypeError):
            self.amp.rotateAng(7)
            self.amp.rotateAng({})

    def test_trim(self):
        # a new test for the trim module
        stlPath = self.get_path("sample_stl_sphere_BIN.stl")
        from AmpScan.core import AmpObject
        Amp = AmpObject(stlPath)
        #with self.assertRaises(TypeError):
            #Amp.planarTrim([], plane=[])

    def test_translate(self):
        # Test translating method of AmpObject

        # Check that everything has been translated correctly to a certain accuracy
        start = self.amp.vert.mean(axis=0)[:]
        self.amp.translate([1, -1, 0])
        end = self.amp.vert.mean(axis=0)[:]
        self.assertAlmostEqual(start[0], end[0]-1, places=TestCore.ACCURACY)
        self.assertAlmostEqual(start[1], end[1]+1, places=TestCore.ACCURACY)
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
        Method to get the absolute path to the testing files

        :param filename: Name of the file in tests folder
        :return: The absolute path to the file
        """

        # Check if the parent directory is tests (this is for Pycharm unittests)
        if os.path.basename(os.getcwd()) == "tests":
            # This is for Pycharm testing
            stlPath = filename
        else:
            # This is for the Gitlab testing
            stlPath = os.path.abspath(os.getcwd()) + "\\tests\\"+filename
        return stlPath

