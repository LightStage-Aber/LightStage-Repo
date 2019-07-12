import unittest
import sys

from test_docker_db import Test_DockerDB
from test_redis_db_on_docker import Test_RedisDBOnDocker
from test_baseline_data_service import Test_BaselineDataService

def check_docker_container_is_up():
    try:
        import docker
        c = docker.from_env()
        con = c.containers.get("ls_redis")
        if not con:
            print("Before running the data service tests, run `sh ../vendor/init_docker_redis.sh`.")
            import sys; sys.exit()
    except Exception as e:
        print("Before running the data service tests: \n- Run `sh ../vendor/init_docker_redis.sh`. (Docker must be installed)")
        import sys; sys.exit()

if __name__ == "__main__":
    check_docker_container_is_up()

    suite1 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_docker_db"] )
    suite2 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_redis_db_on_docker"] )
    suite3 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_baseline_data_service"] )
    
    unittest.TextTestRunner(verbosity=3).run(suite1)
    unittest.TextTestRunner(verbosity=3).run(suite2)
    unittest.TextTestRunner(verbosity=3).run(suite3)

