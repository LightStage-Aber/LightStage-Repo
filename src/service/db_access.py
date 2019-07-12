import redis
import backoff
from docker_connector import ConnectToDocker


from registered_shutdown import GracefulShutdown

class ABC_NOSQL_DB:
    def get_connection(self):
        pass
    def get_series(self, key_list):
        pass
    def set_series(self, zip_data):
        pass
    def get(self, key):
        pass
    def set(self, key, value):
        pass


class RedisDB(ABC_NOSQL_DB):
    """
        Docs: https://github.com/andymccurdy/redis-py/blob/master/redis/client.py
        Text Docs: https://pypi.org/project/redis/
        Getting started: https://redis.io/topics/quickstart

        Caching for CherryPy with Redis: https://bitbucket.org/Lawouach/cherrypy-recipes/src/tip/web/caching/redis_caching/
    """
    def __init__(self, ip=None, port=6379, db=0, *args, **kwords):
        self.pool = None
        self.ip = ip
        self.port = port
        self.db = db
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def get_connection(self):
        if self.pool is None:
            self.pool = redis.ConnectionPool(host=self.ip, port=self.port, db=self.db)
        self.conn = redis.Redis(connection_pool=self.pool)
        return self.conn
    
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def get_series(self, key_list):
        """
            Atomic transaction, typically faster than multiple TCP handshakes.
            
            For more complicated transactions, use r.transaction() for boilerplate removal of pipe.watch(), using callback func.
            See source: https://pypi.org/project/redis/
        """
        conn = self.get_connection()
        pipe = conn.pipeline()
        for k in key_list:
            pipe.get(k)
        res = pipe.execute() 
        return res
  
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def set_series(self, zip_data):
        """
            Atomic transaction, typically faster than multiple TCP handshakes.
            
            For more complicated transactions, use r.transaction() for boilerplate removal of pipe.watch(), using callback func.
            See source: https://pypi.org/project/redis/
        """
        conn = self.get_connection()
        pipe = conn.pipeline()
        d = zip_data.items() if type(zip_data) is dict else zip_data # if dict, return as [(k,v),..] pairs, else assume is already kv pairs.
        for k,v in d:
            pipe.set(k, v)
        return pipe.execute()

    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def get(self, key):
        """
            Get Wrapper
        """
        conn = self.get_connection()
        return conn.get(key)
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def set(self, key, value):
        """
            Set Wrapper
        """
        conn = self.get_connection()
        return conn.set(key, value)

    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def _flushdb(self):
        """
            flushdb Wrapper to empty db
        """
        conn = self.get_connection()
        conn.flushdb()


class RedisDBOnDocker(RedisDB):
    def __init__(self, ip=None, port=6379, db=0, *args, **kwords):
        #RedisDB.__init__(self, ip, port, db, *args, **kwords)
        self.pool = None
        self.dock = ConnectToDocker()
        self.ip = self.dock.get_container_ip()
        self.port = port
        self.db = db

class DBADO(RedisDBOnDocker):
    def __init__(self, *args, **kwords):        
        RedisDBOnDocker.__init__(self, *args, **kwords)