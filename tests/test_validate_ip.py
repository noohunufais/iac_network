import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../flask')))

import unittest
from validate_ip import check_ip

class TestCheckIP(unittest.TestCase):

    def test_invalid_ip(self):

        self.assertFalse(check_ip('')) 
        self.assertFalse(check_ip(' ')) 
        self.assertFalse(check_ip('256.256.256.256'))  
        self.assertFalse(check_ip('1.2.3.4.5')) 
        self.assertFalse(check_ip('192.168.1.')) 
        self.assertFalse(check_ip('one.two.three.four')) 

if __name__ == '__main__':
    unittest.main()