from collections import namedtuple
import json

from options import getPropertiesFile, get_parsed_commandline_options
from db_service import BaselineDataService, ConfigurationDataService

class WSDataProcessor:
    
    def __init__(self):
        self.baseline_data = BaselineDataService()
        self.config_data = ConfigurationDataService()

    def get_baseline_intensities(self):
        return json.dumps( self.baseline_data.get_default_intensities() )

    def get_config_data(self):
        [d,o,a] = self.config_data.get_config_data()
        s = "<h3>Demo Configuration Data:</h3><br>"
        s += "Properties: "+str((d))
        s +="\n"
        s += "Options: "+str(o)
        s += "Arguments: "+str(a)
        s = s.replace("{","<br>{<br>").replace(",",",<br>").replace("}","<br>}<br>")
        return s


