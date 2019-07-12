import subprocess, os

from registered_shutdown import RegisteredShutdown, GracefulShutdown



class WebServiceProcessForker(RegisteredShutdown):
    """
        Start the web service in a new process.
    """
    def __init__(self):
        print("Attempting to start local CherryPy web service.")
        self.web_service_process = None
        try:
            with open(os.devnull, 'w') as fp:
                self.web_service_process = subprocess.Popen(["python", "service_ws.py"], 
                                                            stdout=fp, 
                                                            stderr=fp) # in background.

            GracefulShutdown.register( self )
        except Exception as e:
            print(e)
            GracefulShutdown.do_shutdown()

    def shutdown(self):
        if self.web_service_process is not None:
            self.web_service_process.terminate() # https://docs.python.org/2/library/subprocess.html#subprocess.Popen.terminate

