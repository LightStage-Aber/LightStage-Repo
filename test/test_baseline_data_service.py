default_path = "../src/"
service_path = "../src/service/"
import sys
sys.path.insert(0, default_path)
sys.path.insert(0, service_path)

import unittest
import json

from db_service import BaselineDataService

class Test_BaselineDataService(unittest.TestCase):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        self.dataservice = BaselineDataService(ip=None, port=6379, db=9)

    def setUp(self):
        self.conn = self.dataservice.get_connection()

    def test_underlying_redis_server_connection_is_up(self):
        """"""
        actual = self.conn.ping()
        expected = True
        self.assertTrue(actual == expected)

    def test_baseline_set(self):
        """"""
        d = [1,2,3]
        self.dataservice.set_default_intensities( d )
        actual = json.loads( self.conn.get( self.dataservice._BASELINE_INTENSITIES ) )
        expected = d
        self.assertTrue(actual == expected)

    def test_baseline_set_get(self):
        """"""
        d = [1,2,3]
        self.dataservice.set_default_intensities( d )
        actual = self.dataservice.get_default_intensities()
        expected = d
        self.assertTrue(actual == expected)

    def tearDown(self):
        conn = self.dataservice.get_connection()
        conn.flushdb()


if __name__ == "__main__":

    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)