import os.path
import ConfigParser
import sys
from option_parser import get_parsed_commandline_options



"""
    --------------------------------------------------------------------------------------------------------------

    --- Public interface functions:

    --------------------------------------------------------------------------------------------------------------
"""


def property_to_boolean(section, key):
    k, v = __get_key_value_pair(section, key)
    assert (v in ["True", "False", True, False]), \
        "The "+str(k)+" value must be either 'True' or 'False': " + str(v) + ". Type: " + str(type(v))
    return True if v == "True" or v == True else False


def property_to_string(section, key):
    k, v = __get_key_value_pair(section, key)
    assert v is not None and type(v) is str, \
        "The "+str(k)+" value must not be None: " + str(v) + ". Type: " + str(type(v))
    return v


def property_to_number(section, key, vmin=None, vmax=None, vtype=int):
    """
    :param section: property section for the value.
    :param key: property section's key for the value.
    :param vmin: must be of type vtype or None.
    :param vmax: must be of type vtype or None.
    :param vtype: type expected.
    :return: type and range checked value from properties config file.
    """
    valid_types = [float, int]
    assert vtype in valid_types, "Function property_to_() only accepts types: "+str(valid_types) + "\n" \
                                   "Property: [%s][%s] -- Min=%f , Max=%f, Type=%s" % (section, key, vmin, vmax, vtype)
    k, v = __get_key_value_pair(section, key)

    try:
        v = vtype(v)
    except ValueError as e:
        typecast_succeeded = False
        assert typecast_succeeded, \
            str(k) + " should be of type " + str(vtype) + ". Value is: " + str(v) + ". Type: " + str(type(v))

    no_range = vmin is None and vmax is None
    min_range = vmin is not None and vmax is None
    max_range = vmin is None and vmax is not None
    full_range = vmin is not None and vmax is not None

    if no_range:
        assert isinstance(v, vtype) ,\
            str(k) + " should be of type " + str(vtype) + ". Value is: " + str(v) + ". Type: " + str(type(v))
    elif min_range:
        assert isinstance(v, vtype) and v >= vmin,\
            str(k) + " should be of type " + str(vtype) + " and [>= " + str(vmin) + "]. Value is:" + str(v) + ". Type: " + str(type(v))
    elif max_range:
        assert isinstance(v, vtype) and v <= vmax,\
            str(k) + " should be of type " + str(vtype) + " and [<= " + str(vmax) + "]. Value is:" + str(v) + ". Type: " + str(type(v))
    elif full_range:
        assert isinstance(v, vtype) and vmin <= v <= vmax,\
            str(k) + " should be of type " + str(vtype) + " and between [" + str(vmin) + "-" + str(vmax) + "]. Value is:" + str(v) + ". Type: " + str(type(v))
    return v





"""
    --------------------------------------------------------------------------------------------------------------

    --- Private / Hidden functions follow:

    --------------------------------------------------------------------------------------------------------------
"""

__CACHED_properties_dict = {}

def _reset_cache():
    """
        For resetting during unit tests.
    """
    global __CACHED_properties_dict
    __CACHED_properties_dict = {}

def getPropertiesFile():
    """
    @deprecated in favour of wrapper property_* functions for specific types.
    """
    return __getPropertiesFile()


def __getPropertiesFile():
    global __CACHED_properties_dict
    Options, Args = get_parsed_commandline_options()
    path_to_file = Options.CONFIG_PROPERTIES_FILEPATH or "../properties/default.properties"
    if path_to_file not in __CACHED_properties_dict:
        __CACHED_properties_dict[path_to_file] = __read_properties_from_file(path_to_file)
    return __CACHED_properties_dict[path_to_file]

def __get_key_value_pair(section, key):
    d = __getPropertiesFile()
    v = d[section][key]
    k = "['" + str(section) + "']['" + str(key) + "']"
    return k, v

def set_once_key_value_pair(section, key, value):
    d = __getPropertiesFile()
    if section in d:
        if key in d[section]:
            pass # already set
        else:
            # New key in existing section, set it:
            d[section][key] = value
    else:
        # New section and key, set it:
        d[section] = {}
        d[section][key] = value


class FileNotFoundError(Exception):
    pass

def __read_properties_from_file(path_to_file="../properties/default.properties"):
    config = ConfigParser.RawConfigParser()
    details_dict = {}
    if os.path.exists( path_to_file ):
        config.read( path_to_file )
        for s in config.sections():
            details_dict[s] = dict(config.items(s))
    else:
        raise FileNotFoundError("Properties file not found: "+str(path_to_file))
    return details_dict



if __name__ == "__main__":
    # print( getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.objfilename'] )
    #print( getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.translation'] )
    # print( getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.scale'] )

    print( property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.niter', vmin=0, vmax=None, vtype=int) ) # 100)
    print( property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.niter_success', vmin=0, vmax=10, vtype=int) ) # 1
    print( property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.lower_bounds', vmin=0.0, vmax=2.0, vtype=float) ) # 0.5
    print( property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.upper_bounds', vmin=0.0, vmax=2.0, vtype=float) ) # 1.5
    print( property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.tc', vmin=0.0, vmax=2.0, vtype=float) ) # 1.0
    print( property_to_boolean(section='BrightnessControlTuner', key='tune.scipy.basinhopping.disp') )
