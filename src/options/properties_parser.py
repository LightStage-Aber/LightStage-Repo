import os.path
import ConfigParser



def getPropertiesFile( path_to_file="config.properties" ):
    
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
    print getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.objfilename']
    print getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.translation']
    print getPropertiesFile( "../../properties/default.properties" )['FrameModel']['frame.scale']
