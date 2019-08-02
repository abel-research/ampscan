"""
Testing suite for basic functionality
"""
import unittest
import os
import sys


class TestBasicFunction(unittest.TestCase):

    def test_setup(self):
        """Tests that the path can be obtained"""
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)

    def test_python_imports(self):
        """Test imports"""
        import numpy, scipy, matplotlib, vtk, AmpScan.core
        s = str(type(numpy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(scipy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(matplotlib))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(vtk))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(AmpScan.core))
        self.assertEqual(s, "<class 'module'>", "Failed import: AmpScan.core")
