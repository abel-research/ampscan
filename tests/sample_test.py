import unittest
import os
import sys
import tests.core_tests
import tests.basic_tests


def suite():
    """
    Get all the unittests for the whole project
    :return: The suite containing the test suites for each module
    """
    s = unittest.TestSuite()
    # Add the tests to the suite
    s.addTest(tests.core_tests.suite())
    s.addTest(tests.basic_tests.suite())
    return s


if __name__ == '__main__':
    # Run the test suites
    unittest.TextTestRunner().run(suite())
