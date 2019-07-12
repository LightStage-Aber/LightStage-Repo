default_path = "../src/"
service_path = "../src/service/"
import sys
sys.path.insert(0, default_path)
sys.path.insert(0, service_path)

import unittest

from docker_connector import ConnectToDocker, BuildRunDocker


class _Config:
    SKIP_SLOW = False

class Test_DockerDB(unittest.TestCase):

    def setUp(self):
        self.dock = ConnectToDocker()

    def test_docker_client_is_up(self):
        """"""
        c = self.dock._connect_to_docker()
        actual = c.ping()
        expected = True
        self.assertTrue(actual == expected)

    @unittest.skipIf(_Config.SKIP_SLOW, "Skipping slow docker test..")
    def test_docker_container_is_returning_meta_data(self):
        """"""
        c = self.dock._connect_to_docker()
        try:
            # Remove any previous hello-world containers, and ignore if not exist.
            container = c.containers.get("hello-world") # will raise if does not exist NotFound or server error APIError
            container.stop(timeout=1)
            container.remove(force=True)
        except Exception as e:
            pass
        # Create and run test container.
        c.images.pull("hello-world")
        c.containers.create("hello-world")
        c.containers.run("hello-world", name="hello-world")
        container = self.dock._ConnectToDocker__get_container(c, "hello-world")
        # Test data:
        actual = vars(c.containers.get("hello-world"))['attrs']["Name"]
        expected = unicode("/hello-world")
        # Tear down:
        container.stop(timeout=1)
        container.remove(force=True)
        # Test:
        self.assertTrue(actual == expected)


class Test_Docker_BuildImageRunContainer(unittest.TestCase):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        self.dock = BuildRunDocker()

    def test_docker_client_is_up(self):
        """"""
        c = self.dock._connect_to_docker()
        actual = c.ping()
        expected = True
        self.assertTrue(actual == expected)


    def test_docker_image_is_created(self):
        """"""
        c = self.dock._connect_to_docker()
        try:
            # Remove any previous hello-world containers, and ignore if not exist.
            container = c.containers.get("hello-world") # will raise if does not exist NotFound or server error APIError
            container.stop(timeout=1)
            container.remove(force=True)
        except Exception as e:
            pass
        # Create and run test container.
        c.images.pull("hello-world")
        c.containers.create("hello-world")
        c.containers.run("hello-world", name="hello-world")
        container = self.dock._ConnectToDocker__get_container(c, "hello-world")

        actual = self.dock.is_image_exist("hello-world")
        expected = True
        self.assertTrue(actual == expected)

    def test_docker_build_image(self):
        """"""
        actual = self.__helper_build_scratch_image("../vendor/test/", "scratch1")
        expected = True
        self.__helper_teardown_container("scratch1")
        self.assertTrue(actual == expected)

    def test_docker_built_image_exists(self):
        """"""
        self.__helper_build_scratch_image("../vendor/test/", "scratch1")
        actual = self.dock.is_image_exist("scratch1")
        expected = True
        self.__helper_teardown_container("scratch1")
        self.assertTrue(actual == expected)
    
    def test_docker_run_container(self):
        """"""
        self.__helper_build_scratch_image("../vendor/test/", "scratch1")
        actual = self.dock.run_container("scratch1")
        expected = True
        self.__helper_teardown_container("scratch1")
        self.assertTrue(actual == expected)
    
    def test_docker_stop_container(self):
        """"""
        self.__helper_build_scratch_image("../vendor/test/", "scratch1")
        self.dock.run_container("scratch1")
        actual = self.dock.stop_container("scratch1")
        expected = True
        self.__helper_teardown_container("scratch1")
        self.assertTrue(actual == expected)
    

    """
            --- Helper Functions ------------------------------------
    """

    def __helper_build_scratch_image(self, path, container_name):
        """ Helper """
        c = self.dock._connect_to_docker()
        try:
            c.images.remove(container_name, force=True)
        except Exception as e:
            pass
        return self.dock.build_image(dockerfile_image_path=path, docker_tag_name=container_name)

    def __helper_teardown_container(self, container_name):
        """ Helper teardown """
        c = self.dock._connect_to_docker()
        try:
            container = c.containers.get(container_name)
            container.stop(timeout=1)
            container.remove(force=True)
        except Exception as e:
            pass

    def rem_images(self):
        c = self.dock._connect_to_docker()
        try:
            c.images.remove("scratch1", force=True)
        except Exception as e:
            pass
        try:
            c.images.remove("hello-world", force=True)
        except Exception as e:
            pass
        try:
            c.images.remove("alpine", force=True)
        except Exception as e:
            pass

    """
            --- Unittest Functions ------------------------------------
    """

    def tearDownModule(self):
        self.rem_images()

    

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
