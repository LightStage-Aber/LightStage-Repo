import sys
from copy import deepcopy
import numpy as np

from shape_validator import checkFaceValidity, checkVerticesValidity, get_array_depth
from service import GracefulShutdown


class CachedObjClass(object):
    def __init__(self, name):
        self.name = name
        self.count = {}
        self.__dict_of_data = {}
    def keys(self):
        return self.__dict_of_data.keys()
    def value(self, key ):
        self.count[key] += 1
        x = self.__dict_of_data[key]
        self.__validate(key, x)
        x = deepcopy(x) if list is type(x) else x # Take a deepcopy of the value if type(list).
        return x
    def __validate(self, key, values):
        depth = get_array_depth( values )
        if depth == 3: # If the structure includes separated obj objects (defined by a 3-layer depth), just merge the objects.
            nparr = np.array(values)
            nparrv = nparr.reshape(-1, nparr.shape[-1])
            # print(str(self.name)+" Cache: "+str(key)+" depth: "+str(len(nparrv.shape)))
            # print("Shape: "+str(nparrv.shape))
            values = nparrv.tolist()
        
        # print(type(values))
        # print(type(values[0]))
        # print(type(values[0][0]))

        if self.name == "faces":
            checkFaceValidity( values )
        elif self.name == "vertices":
            checkVerticesValidity( values )
        # None_invalid = all([i is not None for i in x[0] ])
        # if not None_invalid:
        #     print("None invalid: "+str(None_invalid))
        #     print(self.name+" Count["+str(key)+"] = "+str(self.count[key]))
        #     GracefulShutdown.do_shutdown()

        # float_values_invalid = all([i[0] is not None for i in x[0] ])
        # if not float_values_invalid:
        #     print("Float Values invalid: "+str(float_values_invalid))
        #     print(self.name+" Count["+str(key)+"] = "+str(self.count[key]))
        #     GracefulShutdown.do_shutdown()

        # length_invalid = all([len(i) >= 3 for i in x[0] ])
        # if not length_invalid:
        #     print("Length invalid: "+str(length_invalid))
        #     print(self.name+" Count["+str(key)+"] = "+str(self.count[key]))
        #     GracefulShutdown.do_shutdown()

    def set_once(self, key , value ):
        if key not in self.__dict_of_data:
            print("Caching "+str(self.name)+" for obj file: "+str(key))
            self.__validate(key, value)
            self.__dict_of_data[key] = deepcopy(value) if list is type(value) else value # Take a deepcopy of the value if type(list).
            self.count[key] = 1
        else:
            pass


class CacheObjManager():
    """
        Local Cache container to avoid multiple OBJ file reads for the same filename. Stores faces and vertices.
    """
    cached_vertices = CachedObjClass("vertices")
    cached_faces = CachedObjClass("faces")
