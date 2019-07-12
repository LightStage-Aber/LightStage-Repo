default_path = "../src/"
service_path = "../src/service/"
import sys
sys.path.insert(0, default_path)
sys.path.insert(0, service_path)

import unittest

from db_access import RedisDBOnDocker

class Test_RedisDBOnDocker(unittest.TestCase):
    
    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        self.redis = RedisDBOnDocker(ip=None, port=6379, db=10)

    def test_redis_server_connection_is_up(self):
        """"""
        c = self.redis.get_connection()
        actual = c.ping()
        expected = True
        self.assertTrue(actual == expected)

    def test_redis_server_connection_db_name_is_correct(self):
        """"""
        c = self.redis.get_connection()
        actual = c.echo("test")
        expected = "test"
        self.assertTrue(actual == expected)

    def test_redis_server_connection_echo(self):
        """"""
        c = self.redis.get_connection()
        actual = c.echo("test")
        expected = "test"
        self.assertTrue(actual == expected)

    def test_redis_server_set(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set(key="test",value="test2")
        actual = c.get("test")
        expected = "test2"

        self.assertTrue(actual == expected)

    def test_redis_server_set_get(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set(key="test",value="test2")
        actual = self.redis.get("test")
        expected = "test2"

        self.assertTrue(actual == expected)
    
    def test_redis_server_set_overwrite_get(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set(key="test",value="test2")
        self.redis.set(key="test",value="test3")
        actual = self.redis.get("test")
        expected = "test3"

        self.assertTrue(actual == expected)

    def test_redis_server_set_series_overwrite(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set_series([("test","test2"),("test","test3")])
        actual = self.redis.get("test")
        expected = "test3"

        self.assertTrue(actual == expected)

    def test_redis_server_set_series_dict(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set_series({"test1":"test2","test2":"test3"})
        actual = self.redis.get("test2")
        expected = "test3"

        self.assertTrue(actual == expected)

    def test_redis_server_set_series_list_tuples(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set_series([("test1","test2"),("test2","test3")])
        actual = self.redis.get("test2")
        expected = "test3"

        self.assertTrue(actual == expected)

    def test_redis_server_set_series_get_series(self):
        """"""
        c = self.redis.get_connection()
        self.redis.set_series([("test1","test2"),("test2","test3")])
        actual = self.redis.get_series(["test2","test1"])
        expected = ["test3","test2"]

        self.assertTrue(actual == expected)

    def tearDown(self):
        c = self.redis.get_connection()
        c.flushdb()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
