"""
Common test utilities
"""
import os


def get_path(filename):
    """Returns the absolute path to a test file

    Parameters
    ----------
    filename : string
        Name of file in tests to get path to

    Returns
    -------
    stl_path : string
        The path to the file
    """

    # Check if the parent directory is tests (this is for Pycharm unittests)
    if os.path.basename(os.getcwd()) == "tests":
        # This is for Pycharm testing
        stl_path = filename
    else:
        # This is for the Gitlab testing
        stl_path = os.path.join(os.path.abspath(os.getcwd()), "tests", filename)
    return stl_path
