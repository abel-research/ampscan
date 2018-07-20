import unittest
 
class TestBasicFunction(unittest.TestCase):
    import numpy, scipy, matplotlib, vtk
    
    def test_running(self):
        self.assertTrue(True)
        print("Running sample_test.py")
 
if __name__ == '__main__':
    unittest.main()