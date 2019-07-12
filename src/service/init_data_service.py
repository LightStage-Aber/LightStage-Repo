import subprocess

from registered_shutdown import RegisteredShutdown, GracefulShutdown
from docker_connector import BuildRunDocker


class DataServiceDockerManager(RegisteredShutdown):
    """
        Start the data service in a new process.
    """
    def __init__(self):
        self.dock = BuildRunDocker()
        self.is_data_service_process_running = False

        self.__REDIS_CONTAINER_NAME = "ls_redis"
        self.__REDIS_IMAGE_PATH = "../vendor/redis/Simple/"
        self.build_run_redis()

    def build_run_redis(self):
        print("Attempting to Run Docker Container with Redis Data Service")
        build_result = self.dock.build_image( self.__REDIS_IMAGE_PATH, self.__REDIS_CONTAINER_NAME)
        if build_result:
            self.is_data_service_process_running = self.dock.run_container(self.__REDIS_CONTAINER_NAME)
            GracefulShutdown.register( self )
        
    def shutdown(self):
        if self.is_data_service_process_running:
            stopped = self.dock.stop_container( self.__REDIS_CONTAINER_NAME )
