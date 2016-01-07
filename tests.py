import os
import unittest

import simulation


class TestAin(unittest.TestCase):
    def test_pattern_ocp(self):
        print('Test - ocp.x detection', end='')
        ain = simulation.Ain('5', True)
        if not  os.path.exists('./ocp.3'):
            os.makedirs('./ocp.3')
        match_folder = ain.find_pattern('./', 'ocp')
        self.assertEqual(match_folder, 'ocp.3')
        print(' - OK')
        os.rmdir('./ocp.3')

    def test_pattern_helper(self):
        print('Test - helper.xy detection', end='')
        ain = simulation.Ain('5', True)
        if not  os.path.exists('./helper.13'):
            os.makedirs('./helper.13')
        match_folder = ain.find_pattern('./', 'helper')
        self.assertEqual(match_folder, 'helper.13')
        print(' - OK')
        os.rmdir('./helper.13')

if __name__ == '__main__':
    unittest.main()
