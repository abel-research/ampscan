import unittest
import os
import sys


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestBasicFunction)


class TestBasicFunction(unittest.TestCase):
    ACCURACY = 3  # The number of decimal places to value accuracy for

    def SetUp(self):
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)

    def test_running(self):
        print("Running sample_test.py")
        self.assertTrue(True)

    def test_python_imports(self):
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

    @unittest.expectedFailure
    def test_failure(self):
        s = str(type("string"))
        self.assertEqual(s, "<class 'module'>")
