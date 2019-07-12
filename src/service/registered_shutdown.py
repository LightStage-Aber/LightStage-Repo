import sys
import signal

class GracefulShutdown:
    _register = []
    
    @staticmethod
    def register(instance):
        """
            Usage: - subprocess.Popen() object containers, should 
                        - extend RegisteredShutdown and override shutdown() and 
                        - register to this method, as follows: 
                from service import GracefulShutdown
                GracefulShutdown.register( self ) 
        """
        if isinstance(instance, RegisteredShutdown): # is of base type: RegisteredShutdown
            GracefulShutdown._register.append( instance )
        else:
            raise TypeError("Registered objects for graceful shutdown MUST be of type `RegisteredShutdown`.")
    
    @staticmethod
    def do_shutdown():
        """
            Usage: - sys.exit() calls are replaced with the following, this links all exit points to this method for uniform handling.
                from service import GracefulShutdown
                GracefulShutdown.do_shutdown()
        """
        print("Shutting down")
        for job in GracefulShutdown._register:
            job.shutdown()
        sys.exit()

class RegisteredShutdown:
    def shutdown(self):
        """
            Implement this method appropriately for the class requiring the registered shutdown.
        """
        pass



class GracefulKiller:
    """
    Callback hooks on signal interrupts.
    Based on http://stackoverflow.com/a/31464349/1910555

    How it works: 
        When SIGINT/TERM signal received, callback to exit_gracefully() is called. 
        Then we execute the registered subproc shutdown and exit.

    Usage: - add into __main__ call graph.
        term = GracefulKiller()        
    """
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        GracefulShutdown.do_shutdown()