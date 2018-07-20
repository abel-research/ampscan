import unittest
import os
import sys

class TestBasicFunction(unittest.TestCase):
    
    def test_running(self):
        print("Running sample_test.py")
        self.assertTrue(True)
    
    def test_python_imports(self):
        import numpy, scipy, matplotlib, vtk
        s = str(type(numpy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(scipy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(matplotlib))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(vtk))
        self.assertEqual(s, "<class 'module'>")

    @unittest.expectedFailure
    def test_failure(self):
        s = str(type("string"))
        self.assertEqual(s, "<class 'module'>")
    
    def test_AmpScan_imports(self):
        print("PATH 0:")
        print(sys.path[0])
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)
        #from modPath import align
        print("Check add new path 0:")
        print(sys.path[0])
        import AmpScan.core
        s = str(type(AmpScan.core))
        print(s)
        self.assertFalse(False)

 
if __name__ == '__main__':
    unittest.main()