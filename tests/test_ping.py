import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../flask')))

import unittest
from connectivity import ping_check

class TestCheckIP(unittest.TestCase):

    def test_router_connectivity(self):

        self.assertFalse(ping_check('10.0.60.1'))  
        self.assertFalse(ping_check('10.0.60.2'))
        self.assertFalse(ping_check('10.0.60.3')) 
        self.assertFalse(ping_check('10.0.60.4')) 

    def test_switch_connectivity(self):

        self.assertFalse(ping_check('10.0.10.11'))  
        self.assertFalse(ping_check('10.0.10.12'))
        self.assertFalse(ping_check('10.0.60.13')) 
        self.assertFalse(ping_check('10.0.60.14')) 


if __name__ == '__main__':
    unittest.main()