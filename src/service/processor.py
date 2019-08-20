from collections import namedtuple
import json

import logging

from options import getPropertiesFile, get_parsed_commandline_options
from db_service import BaselineDataService, ConfigurationDataService
from db_lighting_sequence_service import DataService_Client_SphericalGradient


class WSDataProcessor:
    
    def __init__(self):
        self.baseline_data = BaselineDataService()
        self.config_data = ConfigurationDataService()
        self.spherical_gradient_data = DataService_Client_SphericalGradient()


    def get_baseline_intensities(self):
        return json.dumps( self.baseline_data.get_default_intensities() )

    def get_spherical_gradient_rotation(self, axis, num_rotations, current_rotation):
        # Check ifexist->return get() lookup data.
        result_data = self.spherical_gradient_data.lookup( axis, num_rotations, current_rotation )
        data_unavailable = result_data is None or result_data is "" or result_data is '\'""\''
        logging.debug(repr(result_data)) #'\'""\''
        logging.debug(type(result_data))
        logging.debug("{}".format(data_unavailable))
        # Check else->publish->[loop:ifexist]->return.
        if not data_unavailable:
            self.spherical_gradient_data.publish_to_service( axis, num_rotations, current_rotation )
            try:
                result_data = self.spherical_gradient_data.lookup_and_wait( axis, num_rotations, current_rotation )
            except Exception:
                result_data = None
        return result_data

    def get_config_data(self):
        [d,o,a] = self.config_data.get_config_data()
        s = "<h3>Demo Configuration Data:</h3><br>"
        s += "Properties: "+str((d))
        s +="\n"
        s += "Options: "+str(o)
        s += "Arguments: "+str(a)
        s = s.replace("{","<br>{<br>").replace(",",",<br>").replace("}","<br>}<br>")
        return s


