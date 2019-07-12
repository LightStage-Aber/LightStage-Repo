import cherrypy, json

from processor import WSDataProcessor


class LSWebService(object):
    
    def __init__(self):
        self.processor = WSDataProcessor()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        data = cherrypy.request.json
        output = self.processor.run(data)
        return json.dumps(output)

    @cherrypy.expose
    def baseline_intensities(self):
        return self.processor.get_baseline_intensities()

    @cherrypy.expose
    def status(self):
        return "okay"

    @cherrypy.expose
    def config(self):
        return self.processor.get_config_data()

    @cherrypy.expose
    def index(self):
        return  '<ul>'+\
                '<li><a href="/status">'+str("status")+'</a></li>'+\
                '<li><a href="/config">'+str("config")+'</a></li>'+\
                '<li><a href="/baseline_intensities">'+str("baseline_intensities")+'</a></li>'+\
                '</ul>'
