import sys, logging
import signal

class GracefulShutdown:
    _register = []
    
    class ServiceContainer:
        def __init__(self, inst, nice):
            self.nice = nice
            self.instance = inst


    @staticmethod
    def register(instance, nice=0):
        """
            Arguments:
            `instance` argument should be an Object of type `RegisteredShutdown`.
            `nice` parameter permits a natural ascending priority-basis for shutdown execution order. Default is 0 (int), no range limitations.
            
            Usage: - subprocess.Popen() object containers, should 
                        - extend RegisteredShutdown and override shutdown() and 
                        - register to this method, as follows:
                from service import GracefulShutdown
                GracefulShutdown.register( self ) # For regular execution shutdown order.
                or 
                GracefulShutdown.register( self, nice=-1 ) # For earlier execution shutdown order.
        """
        if isinstance(instance, RegisteredShutdown): # is of base type: RegisteredShutdown
            container = GracefulShutdown.ServiceContainer(instance, nice)
            GracefulShutdown._register.append( container )
        else:
            raise TypeError("Registered objects for graceful shutdown MUST be of type `RegisteredShutdown`.")
    
    @staticmethod
    def do_shutdown():
        """
            Usage: - sys.exit() calls are replaced with the following, this links all exit points to this method for uniform handling.
                from service import GracefulShutdown
                GracefulShutdown.do_shutdown()
        """
        logging.info("Shutting down services:")
        GracefulShutdown._register.sort( key=lambda x: x.nice )
        qty = len(GracefulShutdown._register)
        for i in range(qty):
            container = GracefulShutdown._register[i]
            job = container.instance
            logging.info("{}/{}. [{}] - {}".format((i+1), qty, container.nice, job.__class__.__name__))
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