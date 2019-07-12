import os
import docker
import ipaddress
import backoff

from registered_shutdown import GracefulShutdown



class ConnectToDocker:
    """
        Class to connect and manage Docker via the py-docker Api.

        - This class is for **read-only** management of Docker resources. (Under container failure it will attempt container restart)
        - See class BuildRunDocker for read/write management of Docker resources.

        Note:   Any changes made should ensure instances (or subclass instances) of 
                this class should NOT retain any open client connections to docker.

        Docs: https://docker-py.readthedocs.io/en/stable/containers.html
    """
    def __init__(self):
        self.ip = None
        self.container_name = "ls_redis"
        self.init_docker_redis_script = "../vendor/init_docker_redis.sh"
        self.stop_docker_redis_script = "../vendor/stop_docker_redis.sh"
        self.restart_docker_redis_cli = "docker container restart ls_redis"
        self.remove_docker_redis_script = "../vendor/remove_docker_redis.sh"
        self.install_docker_script = "../vendor/install_docker.sh"

    def get_container_ip(self):
        if self.ip is None:
            client = self._connect_to_docker()
            container = self.__get_container(client, self.container_name)
            self.ip = self.__get_container_ip(container, self.container_name)
        return self.ip

    def _connect_to_docker(self):
        client = None
        try:
            # Reference: https://docker-py.readthedocs.io/en/stable/client.html
            # Library: https://github.com/docker/docker-py
            client = docker.from_env()
            if client is None:
                raise Exception
        except Exception as e:
            print("Something went wrong connecting to docker.. Perhaps docker is not installed or permission is not granted to access docker..")
            print("You could try:")
            print(" Check status with 'docker images' and 'docker container ls' to view the built images and running containers (-a for all). Our image and container have the name: "+str(container_name))
            print(" Manual docker install and set the user environment for docker with the script: '"+str(self.install_docker_script)+"' (Linux/Unix/Mac only)")
            print("")
            GracefulShutdown.do_shutdown()
        return client

    def is_container_up(self, tag_name=None):
        tag_name = tag_name or self.container_name
        client = self._connect_to_docker()
        try:
            # Reference: https://docker-py.readthedocs.io/en/stable/containers.html
            container = client.containers.get(tag_name)
        except Exception as e:
            container = False
        return container


    @backoff.on_exception(backoff.fibo,
                      (docker.errors.NotFound,
                      docker.errors.APIError),
                      max_time=10,
                      giveup=lambda e: None)
    def _wrapped_get_container(self, client, container_name):
        return client.containers.get(container_name)

    def __get_container(self, client, container_name):
        container = None
        try:
            # Reference: https://docker-py.readthedocs.io/en/stable/containers.html
            container = self._wrapped_get_container(client, container_name)
            if container is None:
                raise Exception
        except Exception as e:
            print("Something went wrong locating our docker container: '"+str(container_name)+"'. Perhaps the image is not yet built or not running.")
            print("You could try:")
            print(" Re-run the application.")
            print(" Restart the container with: '"+str(self.restart_docker_redis_cli)+"' (any OS)")
            print(" Check status with 'docker images' and 'docker container ls' to view the built images and running containers (-a for all). Our image and container have the name: "+str(container_name))
            print(" Removal script for docker container/image: '"+str(self.remove_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print(" Init script for docker image/container: '"+str(self.init_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("")
            GracefulShutdown.do_shutdown()
        return container


    @backoff.on_exception(backoff.fibo,
                      (ValueError, 
                      ipaddress.AddressValueError),
                      max_time=10)
    def _wrapped_get_ip(self, container):
        # Source adapted from: https://stackoverflow.com/a/51889812/1910555
        ip = vars( container )["attrs"]["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
        ipaddress.ip_address(unicode(ip)) # validate the ip or raise ValueError.
        return ip

    @backoff.on_exception(backoff.fibo,
                      (docker.errors.APIError),
                      max_time=5)
    def _wrapped_restart_container(self, container):
        container.restart()
        return True

    def __get_container_ip(self, container, container_name):
        ip = None
        try:
            ip = self._wrapped_get_ip(container)
        except ValueError as e:
            print("Attempting container restart and retry get ip")
            try:
                is_restart_successful = self._wrapped_restart_container(container)  # True or Exception thrown
                if is_restart_successful:
                    ip = self._wrapped_get_ip(container)
                if ip is None:
                    raise Exception
            except Exception as e:
                print("Something went wrong locating or validating the IP address of our docker container: '"+str(container_name)+"'.")
                print("Perhaps the container is not running or the image failed to complete its build correctly.")
                print("You could try:")
                print(" Re-run the application.")
                print(" Restart the container with: '"+str(self.restart_docker_redis_cli)+"' (any OS)")
                print(" Check status with 'docker images' and 'docker container ls' to view the built images and running containers (-a for all). Our image and container have the name: "+str(container_name))
                print(" Removal script for docker container/image: '"+str(self.remove_docker_redis_script)+"' (Linux/Unix/Mac only)")
                print(" Init script for docker image/container: '"+str(self.init_docker_redis_script)+"' (Linux/Unix/Mac only)")
                print("")
                print("Report from exception: "+str(e))
                GracefulShutdown.do_shutdown()
        return ip




class BuildRunDocker(ConnectToDocker):
    """
        Specialised class to build images and run/stop containers.
    """
    def __init__(self, *args, **kwords):
        ConnectToDocker.__init__(self, *args, **kwords)

    def is_image_exist(self, docker_tag_name):
        image_exists = False
        client = self._connect_to_docker()
        try:
            res = client.images.list(name=docker_tag_name)
            image_exists = len(res) >= 1
        except docker.errors.APIError as e:         # If the server returns an error.
            image_exists = False
        return image_exists

    def build_image(self, dockerfile_image_path, docker_tag_name):
        is_image_built = False
        client = self._connect_to_docker()
        try: 
            if not self.is_image_exist(docker_tag_name):
                print("Attempting to pull docker images from online, specified in "+str(dockerfile_image_path)+"Dockerfile")
                # cd redis/Simple
                # docker build -t $REDIS_CONTAINER_NAME .
                image = client.images.build(path=dockerfile_image_path, tag=docker_tag_name)
            is_image_built = True
        except docker.errors.BuildError as e:   #  If there is an error during the build.
            print("There was an error during the build of our docker image: '"+str(docker_tag_name)+"'")
            print("Dockerfile at path: "+str(dockerfile_image_path)+" exists (bool): "+ str(os.path.exists(dockerfile_image_path)))
            print("You could try manually initialising the image and container with this script: '"+str(self.init_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("Or you could manually remove the image and container with this script (before init): '"+str(self.remove_docker_redis_script)+"' (Linux/Unix/Mac only)")            
            print("")
            print("To help diagnose, run 'docker images' and 'docker container ls' to view the built images and running containers. Our image and container have the tag name: "+str(docker_tag_name))
            GracefulShutdown.do_shutdown()
        except docker.errors.APIError as e:     # If the server returns any other error.
            print("The docker server returned an error, while we attempted to build our docker image: '"+str(docker_tag_name)+"'")
            print("")
            print("Perhaps docker is not installed or access permission is not granted for docker..")
            print("You could try manually installing and setting the user environment for docker with the script: '"+str(self.install_docker_script)+"'")
            print("")
            print("Run 'docker images' and 'docker container ls' to view the built images and running containers.")
            GracefulShutdown.do_shutdown()
        return is_image_built

    def run_container(self, docker_tag_name):
        is_data_service_process_running = False
        client = self._connect_to_docker()
        try:
            if not self.is_container_up(docker_tag_name):
                # docker run --name $REDIS_CONTAINER_NAME -d $REDIS_CONTAINER_NAME
                client.containers.run(image=docker_tag_name, name=docker_tag_name, detach=True)
            is_data_service_process_running = True
        except docker.errors.APIError as e:         # If the server returns an error.
            print("The docker server returned an error, while we attempted to run our docker container: '"+str(docker_tag_name)+"'")
            print("")
            print("Perhaps docker is not installed, docker has some conflict or access permission is not granted for docker..")
            print("You could try manually installing and setting the user environment for docker with the script: '"+str(self.install_docker_script)+"'")
            print("")
            print("Run 'docker images' and 'docker container ls' to view the built images and running containers.")
            GracefulShutdown.do_shutdown()
        except docker.errors.ImageNotFound as e:    # If the specified image does not exist.
            print("Docker reports that the specified image does not exist: '"+str(docker_tag_name)+"'")
            print("You could manually run the image/container removal script: '"+str(self.remove_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("Then manually run the image/container init script: '"+str(self.init_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("")
            print("Run 'docker images' and 'docker container ls' to view the built images and running containers. Our image and container have the name: "+str(docker_tag_name))
            GracefulShutdown.do_shutdown()
        except docker.errors.ContainerError as e:   # If the container exits with a non-zero exit code and detach is False.
            print("Something went wrong while running the docker container: '"+str(docker_tag_name)+"'")
            print("You could manually run the image/container removal script: '"+str(self.remove_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("Then manually run the image/container init script: '"+str(self.init_docker_redis_script)+"' (Linux/Unix/Mac only)")
            print("")
            print("Run 'docker images' and 'docker container ls' to view the built images and running containers. Our image and container have the name: "+str(docker_tag_name))
            GracefulShutdown.do_shutdown()
        return is_data_service_process_running

    def stop_container(self, docker_tag_name):
        container_stopped = False
        client = self._connect_to_docker()
        if self.is_container_up(docker_tag_name):
            try:
                cont = client.containers.get(docker_tag_name)
                cont.stop()
                cont.remove(force=True)
                container_stopped = True
            except docker.errors.APIError as e:         # If the server returns an error.
                pass
            except Exception as e:                      # Some other error during shutdown, non-blocking shutdown.
                pass
        return container_stopped

