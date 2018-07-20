import unittest
 
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
 
if __name__ == '__main__':
    unittest.main()