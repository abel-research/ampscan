import unittest
import os
import sys

class TestBasicFunction(unittest.TestCase):
    
    def test_running(self):
        print("Running sample_test.py")
        self.assertTrue(True)
    
    def test_python_imports(self):
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)
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
        self.assertEqual(s, "<class 'module'>")

    @unittest.expectedFailure
    def test_failure(self):
        s = str(type("string"))
        self.assertEqual(s, "<class 'module'>")

    def test_import_stl(self):
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)
        from AmpScan.core import AmpObject
        from AmpScan.tests import sample_stl_sphere as stlFile
        Amp = AmpObject(stlFile)
        self.assertRaises(MemoryError)

if __name__ == '__main__':
    unittest.main()
