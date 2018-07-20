import unittest
 
class TestBasicFunction(unittest.TestCase):
    
    def test_running(self):
        print("Running sample_test.py")
        self.assertTrue(True)
    
    def test_imports(self):
        import numpy, scipy, matplotlib, vtk
        s = str(type(numpy))
        self.assertEqual(s, "<class 'module'>")
 
if __name__ == '__main__':
    unittest.main()