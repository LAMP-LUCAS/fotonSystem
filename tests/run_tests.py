import unittest
import sys
import os

if __name__ == '__main__':
    # Add project root to path (Two levels up from tests/run_tests.py)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    
    # Define tests directory explicitly
    tests_dir = os.path.join(project_root, 'tests')
    
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(not result.wasSuccessful())
