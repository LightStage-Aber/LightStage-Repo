import unittest
import sys

from test_docker_db import Test_DockerDB
from test_redis_db_on_docker import Test_RedisDBOnDocker
from test_baseline_data_service import Test_BaselineDataService
from test_PLOS_ONE_Article_Repulsion_EXPS_May2017 import PLOSOneEXP_Repulsion_LettvinOnly
from test_PLOS_ONE_Article_Control_MC_EXPS_May2017 import PLOSOneEXP_Controls, PLOSOneEXP_MonteCarlo
from test_PLOS_ONE_Article_MonteCarlo_Tuning_EXPS_May2017 import Test_IterativeRegression
from test_model_objects import Test_DomeModel
from test_BrightnessControl import Test_IterativeRegression, Test_SciPyBasinHopping



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

    # Data Service
    suite1 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_docker_db"] )
    suite2 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_redis_db_on_docker"] )
    suite3 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_baseline_data_service"] )
    
    unittest.TextTestRunner(verbosity=3).run(suite1)
    unittest.TextTestRunner(verbosity=3).run(suite2)
    unittest.TextTestRunner(verbosity=3).run(suite3)

    # Module tests (+Subsystem)
    suite4 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_model_objects"] )
    suite5 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_PLOS_ONE_Article_Control_MC_EXPS_May2017"] )
    suite6 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_PLOS_ONE_Article_MonteCarlo_Tuning_EXPS_May2017"] )
    
    unittest.TextTestRunner(verbosity=3).run(suite4)
    unittest.TextTestRunner(verbosity=3).run(suite5)
    unittest.TextTestRunner(verbosity=3).run(suite6)

    # Slower Module tests  (Subsystem)
    # suite7 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_PLOS_ONE_Article_Repulsion_EXPS_May2017"] )
    suite99 = unittest.TestLoader().loadTestsFromModule( sys.modules["test_BrightnessControl"] )

    # unittest.TextTestRunner(verbosity=3).run(suite7)
    unittest.TextTestRunner(verbosity=3).run(suite99)

