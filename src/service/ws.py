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
    def spherical_gradient(self, axis="x", num_rotations=1, current_rotation=-1):
        res = self.processor.get_spherical_gradient_rotation( 
            axis, num_rotations, current_rotation
         )
        if res is None:
            raise cherrypy.HTTPError(404)
        else:
            return json.dumps( res )

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
                '<li><a href="/spherical_gradient?axis=x&num_rotations=5&current_rotation=1">'+str("spherical_gradient")+'</a></li>'+\
                '</ul>'
                