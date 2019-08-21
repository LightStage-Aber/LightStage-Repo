import redis, logging
import backoff
from docker_connector import ConnectToDocker


from registered_shutdown import GracefulShutdown, RegisteredShutdown

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
    def report_set_key(self, k,v):
        logging.debug("Redis: {} = {}".format(k, v))


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
        self.report_set_key(res,"")
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
            self.report_set_key(k,v)
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
        v = conn.get(key)
        self.report_set_key(key,v)
        return v
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def set(self, key, value):
        """
            Set Wrapper
        """
        conn = self.get_connection()
        self.report_set_key(key,value)
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

class DBADO_ThreadedPubSub(RedisDBOnDocker, RegisteredShutdown):
    """
        Class wrapper to execute threaded pubsub messaging via redis.
    """
    def __init__(self, *args, **kwords):        
        RedisDBOnDocker.__init__(self, *args, **kwords)
        self._thread = None
        self._pubsub = None
        GracefulShutdown.register( self, nice=-5 ) 
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def subscribe(self, key, callback_func):
        """
            Subscribe Wrapper, with callback function run in own thread.
            Thread shutdown, via GracefulShutdown.register(self) in init().
        """
        r = self.get_connection()
        self._pubsub = r.pubsub()
        self._pubsub.subscribe( **{key:callback_func} )
        self._thread = self._pubsub.run_in_thread(sleep_time=0.1)
    
    @backoff.on_exception(backoff.fibo,
                      redis.exceptions.ConnectionError,
                      max_time=10)
    def publish(self, key, message):
        """
            Publish Wrapper
        """
        conn = self.get_connection()
        return conn.publish( key, message)
        
    def shutdown(self):
        try:
            self._thread.stop()
            logging.debug("subscription thread stop() called. Waiting for join.")
            self._thread.join()
            logging.debug("subscription thread terminated and joined.")
        except Exception as e:
            logging.warning("subscription thread failed during stop() or join().")
        try:
            self._pubsub.close()
            logging.debug("subscription redis.pubsub channel closed.")
        except Exception as e:
            logging.warning("subscription redis.pubsub channel failed during close().")