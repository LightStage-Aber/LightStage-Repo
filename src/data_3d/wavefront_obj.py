import numpy as np
import os


from obj_cache_manager import CacheObjManager
import dome_obj_data
from shape_validator import checkShapeValidity, checkVerticesValidity
from obj_model_reader import get_all_object_polyfaces, read_vertices_objects, apply_scale, read_faces_objects

class WaveFront:
    def __init__(self):
        CacheObjManager()
    

    @staticmethod
    def get_shape( filename, scale, translation=(0,0,0) ):
        return get_all_object_polyfaces( filename, scale, translation )
    
    @staticmethod
    def get_frame( filename, scale ):
        # load in frame vertex positions as leds
        frame = read_vertices_objects(filename)[0]
        apply_scale(frame, scale)
        assert len(frame) > 0, "Frame loaded from .obj file %s" % (str(self._frame_objfilename))
        return frame

    @staticmethod
    def get_hardcoded_frame( scale ):
        # edges = dome_obj_data.get_dome_faces()
        vertices = dome_obj_data.get_dome_vertices()
        r = [x[1:]  for x in vertices]
        
        #Nastily apply scaling to vertices for return variable.
        r2 = []
        for i in range(len(r)):
            r2.append([])
            for j in range(len(r[i])):
                r2[i].append(  r[i][j]* scale )
        r = r2
        nparr = np.array(r)
        # print("Hardcoded frame: "+str(nparr.shape))
        checkVerticesValidity( r )
        return r


    @staticmethod
    def get_hardcoded_frame_faces():
        return dome_obj_data.get_dome_faces()

    @staticmethod
    def get_loaded_frame_faces(filename):
        return read_faces_objects(filename)[0]

    @staticmethod
    def get_target_shape(filename=None, scale=None, translation=None):
        # Use defaults if None values provided
        translation = translation or (0,0,0)
        scale = scale or 1
        filename = filename or "../models/dome/dome_c.obj"
        # Load the shape data
        shape_name = os.path.basename(filename)
        triangles = get_all_object_polyfaces( filename, scale, translation )
        # checkShapeValidity( triangles ) # Already validated in cache recall and on load.
        return triangles, shape_name



    # @staticmethod
    # def get_vertices():
    #     pass

    # @staticmethod
    # def get_edges():
    #     """
    #         Wrapper for get_faces()
    #     """
    #     pass

