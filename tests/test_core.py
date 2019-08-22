"""
Testing suite for the core module
"""

import unittest
import numpy as np
from random import randrange
from util import get_path
from AmpScan import analyse


class TestCore(unittest.TestCase):
    ACCURACY = 5  # The number of decimal places to value accuracy for - needed due to floating point inaccuracies

    def setUp(self):
        """Runs before each unit test.
        Sets up the AmpObject object using "stl_file.stl".
        """
        from AmpScan.core import AmpObject
        stl_path = get_path("stl_file.stl")
        self.amp = AmpObject(stl_path)

    def test_centre(self):
        """Test the centre method of AmpObject"""

        # Translate the mesh
        self.amp.translate([1, 0, 0])
        # Recenter the mesh
        self.amp.centre()
        centre = self.amp.vert.mean(axis=0)

        # Check that the mesh is centred correctly (to at least the number of decimal places of ACCURACY)
        self.assertTrue(all(centre[i] < (10**-TestCore.ACCURACY) for i in range(3)))

    def test_centre_static(self):

        with self.assertRaises(TypeError):
            self.amp.centreStatic(1)
        with self.assertRaises(TypeError):
            self.amp.centreStatic([])

        # Import second shape
        from AmpScan.core import AmpObject
        stl_path = get_path("stl_file_2.stl")
        amp2 = AmpObject(stl_path)

        self.amp.centreStatic(amp2)

        for i in range(3):
            # This method has a large degree of error so, it's only testing to 2 dp
            self.assertAlmostEqual(self.amp.vert.mean(axis=0)[i], amp2.vert.mean(axis=0)[i], 2)

    def test_rotate_ang(self):
        """Tests the rotateAng method of AmpObject"""

        # Test rotation on random node
        n = randrange(len(self.amp.vert))
        rot = [0, 0, np.pi/3]
        before = self.amp.vert[n].copy()
        self.amp.rotateAng(rot)
        after_vert_pos = self.amp.vert[n].copy()
        # Use 2D rotation matrix formula to test rotate method on z axis
        expected = [np.cos(rot[2])*before[0]-np.sin(rot[2])*before[1], np.sin(rot[2])*before[0]+np.cos(rot[2])*before[1], before[2]]
        # Check all coordinate dimensions are correct
        all(self.assertAlmostEqual(expected[i], after_vert_pos[i], TestCore.ACCURACY) for i in range(3))

        # Check single floats cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotateAng(7)

        # Check dictionaries cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotateAng(dict())

        # Tests that incorrect number of elements causes ValueError
        with self.assertRaises(ValueError):
            self.amp.rotateAng(rot, "test")
        with self.assertRaises(ValueError):
            self.amp.rotateAng(rot, [])

    def test_rotate(self):
        """Tests the rotate method of AmpObject"""
        # A test rotation and translation using list
        m = [[1, 0, 0], [0, np.sqrt(3)/2, 1/2], [0, -1/2, np.sqrt(3)/2]]
        self.amp.rotate(m)

        # Check single floats cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotate(7)

        # Check dictionaries cause TypeError
        with self.assertRaises(TypeError):
            self.amp.rotate(dict())

        # Check invalid dimensions cause ValueError
        with self.assertRaises(ValueError):
            self.amp.rotate([])
        with self.assertRaises(ValueError):
            self.amp.rotate([[0, 0, 1]])
        with self.assertRaises(ValueError):
            self.amp.rotate([[], [], []])

    def test_translate(self):
        """Test translating method of AmpObject"""

        # Check that everything has been translated correctly to a certain accuracy
        start = self.amp.vert.mean(axis=0).copy()
        self.amp.translate([1, -1, 0])
        end = self.amp.vert.mean(axis=0).copy()
        self.assertAlmostEqual(start[0]+1, end[0], places=TestCore.ACCURACY)
        self.assertAlmostEqual(start[1]-1, end[1], places=TestCore.ACCURACY)
        self.assertAlmostEqual(start[2], end[2], places=TestCore.ACCURACY)

        # Check that translating raises TypeError when translating with an invalid type
        with self.assertRaises(TypeError):
            self.amp.translate("")

        # Check that translating raises ValueError when translating with 2 dimensions
        with self.assertRaises(ValueError):
            self.amp.translate([0, 0])

        # Check that translating raises ValueError when translating with 4 dimensions
        with self.assertRaises(ValueError):
            self.amp.translate([0, 0, 0, 0])

    def test_rigid_transform(self):
        """Test the rigid transform method of AmpObject"""

        # Test if no transform is applied, vertices aren't affected
        before_vert = self.amp.vert.copy()
        self.amp.rigidTransform(R=None, T=None)
        all(self.assertEqual(self.amp.vert[y][x], before_vert[y][x])
            for y in range(len(self.amp.vert))
            for x in range(len(self.amp.vert[0])))

        # A test rotation and translation
        m = [[1, 0, 0], [0, np.sqrt(3)/2, 1/2], [0, -1/2, np.sqrt(3)/2]]
        self.amp.rigidTransform(R=m, T=[1, 0, -1])

        # Check that translating raises TypeError when translating with an invalid type
        with self.assertRaises(TypeError):
            self.amp.rigidTransform(T=dict())

        # Check that rotating raises TypeError when translating with an invalid type
        with self.assertRaises(TypeError):
            self.amp.rigidTransform(R=7)

    def test_rot_matrix(self):
        """Tests the rotMatrix method in AmpObject"""

        # Tests that a transformation by 0 in all axis is 0 matrix
        all(self.amp.rotMatrix([0, 0, 0])[y][x] == 0
            for x in range(3)
            for y in range(3))

        expected = [[1, 0, 0], [0, np.sqrt(3)/2, 1/2], [0, -1/2, np.sqrt(3)/2]]
        all(self.amp.rotMatrix([np.pi/6, 0, 0])[y][x] == expected[y][x]
            for x in range(3)
            for y in range(3))

        # Tests that string passed into rot causes TypeError
        with self.assertRaises(TypeError):
            self.amp.rotMatrix(" ")
        with self.assertRaises(TypeError):
            self.amp.rotMatrix(dict())

        # Tests that incorrect number of elements causes ValueError
        with self.assertRaises(ValueError):
            self.amp.rotMatrix([0, 1])
        with self.assertRaises(ValueError):
            self.amp.rotMatrix([0, 1, 3, 0])

    def test_flip(self):
        """Tests the flip method in AmpObject"""
        # Check invalid axis types cause TypeError
        with self.assertRaises(TypeError):
            self.amp.flip(" ")
        with self.assertRaises(TypeError):
            self.amp.flip(dict())

        # Check invalid axis values cause ValueError
        with self.assertRaises(ValueError):
            self.amp.flip(-1)
        with self.assertRaises(ValueError):
            self.amp.flip(3)

