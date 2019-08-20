"""
    Warning: DO NOT EXECUTE THIS SCRIPT.

    This Py script initialises the web service interface, however:
        * It is invoked by a `subprocess.Popen()` call within the main application call graph.
        * As an application user, there should be no reason to execute this Py script directly.
"""
import cherrypy
from service import LSWebService
import logging

if __name__ == '__main__':
    
    logging.basicConfig(format='%(message)s',level=logging.INFO)
    config = {'server.socket_host': 'localhost'}
    cherrypy.config.update(config)
    cherrypy.quickstart(LSWebService())