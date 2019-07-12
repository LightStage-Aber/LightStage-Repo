import json

from options import getPropertiesFile, get_parsed_commandline_options
from db_access import DBADO

class BaselineDataService(DBADO):
    
    def __init__(self, *args, **kwords):
        DBADO.__init__(self, *args, **kwords)
        self._BASELINE_INTENSITIES = "baseline_intensities"

    def set_default_intensities(self, intensities_data):
        json_data = json.dumps( intensities_data, separators=(',',':') )
        return self.set( self._BASELINE_INTENSITIES, json_data )

    def get_default_intensities(self):
        json_data = self.get( self._BASELINE_INTENSITIES )
        return json.loads( json_data )


class ConfigurationDataService(DBADO):
    
    def __init__(self, *args, **kwords):
        DBADO.__init__(self, *args, **kwords)
        self._CONFIG_PROPERTIES = "CONFIG_PROPERTIES"
        self._CONFIG_OPTIONS = "CONFIG_OPTIONS"
        self._CONFIG_ARGUMENTS = "CONFIG_ARGUMENTS"
    
    def set_config_data(self):
        d = getPropertiesFile()
        o,a = get_parsed_commandline_options()
        data = {
            self._CONFIG_PROPERTIES: json.dumps( d , separators=(',',':') ),
        # Options from optparse returns an Object, so get its dict. @todo this is hack, move to non deprecated argparse, and handle object->json correctly.
            self._CONFIG_OPTIONS: json.dumps( o, separators=(',',':'), default=lambda o: o.__dict__),
            self._CONFIG_ARGUMENTS: json.dumps( a , separators=(',',':')),
        }
        return self.set_series( data )

    def get_config_data(self):
        [_d,_o,_a] = self.get_series( [
                self._CONFIG_PROPERTIES,
                self._CONFIG_OPTIONS,
                self._CONFIG_ARGUMENTS,
            ])
        d,o,a = json.loads( _d ), json.loads( _o ), json.loads( _a )
        return d,o,a

