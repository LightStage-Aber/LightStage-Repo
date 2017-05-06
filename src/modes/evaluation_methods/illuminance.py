from __future__ import print_function

"""
    Illuminance Module:
    - Module containing algorithmic approaches that quantify based on amount of "light hitting the surface of a target object".
"""

from __future__ import division
import random as rnd
import time;     currentMillis = lambda: int(round(time.time() * 1000))
import os
from itertools import chain; flatten_x = lambda x: list(chain.from_iterable(x));

import logging
logging.basicConfig(format='%(message)s')

from datastructures.orderedset import OrderedSet, ListHashableOrderedSet
from options import getPropertiesFile
from file_utils import file_io
from data_3d.obj_model_reader import get_all_vertex_face_objects, apply_scale, get_triangle_centers, read_vertices_objects, read_faces_objects
from data_3d.dome_obj_data import get_dome_faces
from ..manipulate_results_data import *
from ..visualisations import *
from ..evaluations import *
from .. import distance_measures
import monte_carlo_sequences
from ..tuning_intensities.tuners import *
from ..tuning_intensities.tuning_selector import *
from helper_illuminance import *


class LoadLEDPositions(object):
    """
    Use this object as a mixin helper class to load in the LED position vertex positions.
    Usage: - In Constructor
        LoadLEDPositions.__init__(self)
        self.leds = self.load_leds_positions()
    """
    def __init__(self):
        dict_properties         = getPropertiesFile( "../properties/default.properties" )
        self._source_filename   = dict_properties['LightPositions']['light.objfilename']
        self._lights_scale            = float(dict_properties['LightPositions']['light.scale'])
        self._path_prefix             = dict_properties['LightPositions']['light.results_output_file_path_prefix']

    def load_leds_positions(self):
        # load in frame vertex positions as leds
        leds = read_vertices_objects( self._source_filename )[0]
        apply_scale( leds, scale=self._lights_scale )
        return leds

class LoadLEDIndexes(object):
    """
    Use this object as a mixin helper class to load in the LED index positions (to then later match with vertex positions).
    Usage: - In Constructor
        LoadLEDIndexes.__init__(self)
        self.leds = self.load_leds_indexes()
    """
    def __init__(self):
        dict_properties         = getPropertiesFile( "../properties/default.properties" )
        self._source_filename   = dict_properties['EvaluateSingleResultsFile']['results_file.csvfilename']
        self._column_number     = int(dict_properties['EvaluateSingleResultsFile']['results_file.column_number'])
        self._number_of_leds    = int(dict_properties['EvaluateSingleResultsFile']['results_file.number_of_leds'])
        self._path_prefix       = dict_properties['EvaluateSingleResultsFile']['results_file.results_output_file_path_prefix']

        assert (os.path.exists(self._source_filename))
        assert (self._column_number >= 0)
        assert (self._number_of_leds > 0)

    @staticmethod
    def get_vertices_from_indexes(indexes, vertices_list):
        led_vertices = []
        for i in indexes:
            if i >= len(vertices_list):
                logging.warn('Warning: request to select LED by an index value that is outside of the known set.')
            else:
                v = vertices_list[i]
                led_vertices.append( v ) if v is not None else None
        return led_vertices

    def load_leds_indexes(self):
        # Load the results file. Return a list of the best index points:
        best_LEDs = file_io.read_in_csv_file_to_list_of_lists(self._source_filename, skip_header=False)
        led_indexes = get_sorted_column_from_result_file(best_LEDs, column_index=self._column_number, qty=self._number_of_leds)
        return led_indexes

class LoadFramePositions(object):
    """
    Use this object as a mixin helper class to load in the LED frame.
    Usage: - In Constructor
        LoadFramePositions.__init__(self, hardcoded_leds=[])
        self.frame = self.get_frame()
    """
    def __init__(self, hardcoded_leds=[]):
        dict_properties = getPropertiesFile("../properties/default.properties")
        self._frame_objfilename = dict_properties['FrameModel']['frame.objfilename']
        self._frame_scale = float(dict_properties['FrameModel']['frame.scale'])
        self.__hardcoded_leds = hardcoded_leds

        self._with_support_access = eval(dict_properties['FrameModel']['frame.withsupportaccess'])
        assert isinstance(self._with_support_access, bool), "[FrameModel] frame.withsupportaccess must be of type 'bool'. " \
                                                      "Found: "+str(type(self._with_support_access))

        self._frame_indexes_are_important = eval(dict_properties['FrameModel']['frame.indexes_are_important'])
        assert isinstance(self._frame_indexes_are_important, bool), "[FrameModel] frame.indexes_are_important must be of type 'bool'. " \
                                                              "Found: "+str(type(self._frame_indexes_are_important))

        assert self.__hardcoded_leds is not None and len(self.__hardcoded_leds) > 0, "Number of hardcoded LEDs should be GT 0. Even if not used."

    def get_frame(self):
        # todo: Warning Hardcoded vs loaded frame is not handled. Currently always loaded from file.
        print("Warning Hardcoded vs loaded frame is not handled. Currently always loaded.")
        if self._frame_indexes_are_important: # Hardcoded / not
            frame = self.get_hardcoded_frame()
        else:
            frame = self.__get_frame_from_obj()
        frame = self.__check_to_apply_support_access(frame)
        return frame

    def get_hardcoded_frame(self):
        return self.__hardcoded_leds

    def get_file_loaded_frame(self):
        return self.__get_frame_from_obj()

    def __get_frame_from_obj(self):
        # load in frame vertex positions as leds
        frame = read_vertices_objects(self._frame_objfilename)[0]
        apply_scale(frame, scale=self._frame_scale)
        return frame

    def __check_to_apply_support_access(self, frame):
        if self._with_support_access:
            frame = self.__remove_bottom_LED_vertex( frame )
        return frame

    def __remove_bottom_LED_vertex(self, frame):
        y_axis = [y for [x, y, z] in frame]
        lowest_y = y_axis.index(min(y_axis))
        frame[lowest_y] = None
        return frame

class LoadEdgeFramePositions(LoadFramePositions):
    """
    Use this object as a mixin helper class to load in the LED frame and split each frame edge into 10 vertex positions.
    Usage: - In Constructor
        LoadEdgeFramePositions.__init__(self, kwords)   # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)
    """
    def __init__(self, kwords):
        LoadFramePositions.__init__(self, hardcoded_leds=kwords['all_leds'])
        self.NUM_OF_VERTICES_PER_EDGE = 11  # --  This number should include the start vertex and end vertex of the edge, as well as the new vertex points along the edge.
        assert (self.NUM_OF_VERTICES_PER_EDGE > 0)

    def get_frame_edge_points(self, frame):
        faces = self.__get_faces()
        return self.__get_frame_edge_points(frame, faces)

    def __get_faces(self):
        # Get edges between vertices, in order to segment each edge into n vertices. We extract this from the tris (faces)
        if self._frame_indexes_are_important:
            faces = get_dome_faces()                                # Load from hardcoded data.
        else:
            faces = read_faces_objects(self._frame_objfilename)[0]  # Load from file.
        return faces

    def __get_frame_edge_points(self, frame, faces):
        # Push each new vertex point into an OrderedSet - This avoids duplicate vertices due to edges starting/ending at
        # matching points and to avoid duplicate points along the two edges with the same start/end vertex points (
        # i.e. the edges of two adjacent triangles).
        global_vertices = ListHashableOrderedSet()

        assert len(faces) > 0, "The number of faces loaded from the OBJ model file specified in [FrameModel] must be GT 0."
        assert isinstance(faces, list), "Faces data expected as iterable. Found: " + str(type(faces))

        # For all faces, we will get the new set of vertices, including existing and the newly calculated vertices that
        # resulted from the edge segmenting
        for triple in faces:
            # - Example of a face triple:
            # frame[triple[0]] == [2.611816, 7.513872, -0.848632]
            # frame[triple[1]] == [0.0, 7.513872, -2.746232]
            # frame[triple[2]] == [-2.611816, 7.513872, -0.848632]

            # Each edge of the face is connected as follows:
            edges = [(0, 1), (1, 2), (2, 0)]

            # If any point on the current face doesn't have a corresponding vertex position, then abort this face.
            if not all([frame[t - 1] is not None for t in triple]):
                continue

            # For all of the edges of this face:
            for edge in edges:

                # start and end of line:
                v1_from = frame[triple[edge[0]] - 1]
                v2_to = frame[triple[edge[1]] - 1]

                # translate to the first point of line:
                v1_start = [0, 0, 0]
                v2_end = [v2_to[0] - v1_from[0], v2_to[1] - v1_from[1], v2_to[2] - v1_from[2]]
                local_vertices = []

                # calculate the first point along the line (excluding start- and end-points)
                v2_unit = [x / (self.NUM_OF_VERTICES_PER_EDGE - 1) for x in v2_end]

                # Divide line by 10. Create a new vertex at (l/10)*1, (l/10)*2, (l/10)*3, .. (l/10)*9,
                for d in range(0, self.NUM_OF_VERTICES_PER_EDGE):
                    v = [x * d for x in v2_unit]
                    local_vertices.append(v)

                    # translate all new local coordinates back into global space, push them onto the ordered set of vertices.
                for i in range(len(local_vertices)):
                    v = local_vertices[i]
                    gv = [v[0] + v1_from[0], v[1] + v1_from[1], v[2] + v1_from[2]]
                    global_vertices.add(gv)

        # Transfer into new list object to return.
        return_frame = list(global_vertices)

        return return_frame





class RawPositionEvaluator(EvaluatorGeneric, LoadLEDPositions, LoadFramePositions):
    """
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model, using a specified set of light vertex positions, i.e. Lettvin's diffuse positions.
    Jan 2017.
    """
    def __init__(self, kwords={}):
        LoadLEDPositions.__init__(self)
        LoadFramePositions.__init__(self, hardcoded_leds=kwords['all_leds'])
        self.leds_vertices = self.load_leds_positions()
        self.frame = self.get_frame()
        self.shortname = "Raw Lettvin Positions"

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)
            
    def evaluate( self, triangles ):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices)

    def tune( self, triangles ):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices)

class VertexMappedPositionEvaluator(RawPositionEvaluator):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor)
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model, using a specified set of light vertex positions, i.e. Lettvin's diffuse positions.
    Jan 2017.
    """
    def __init__(self, kwords):
        LoadLEDPositions.__init__(self)
        LoadFramePositions.__init__(self, hardcoded_leds=kwords['all_leds'])
        self.leds_vertices = self.load_leds_positions()
        self.frame = self.get_frame()
        self.leds_vertices = self.map_to_frame( self.frame )

        self.shortname = "Mapped to dome vertices ("+str(len(self.frame))+" points)"

    def map_to_frame(self, frame):
        
        mappings = {}
        for v1 in self.leds_vertices:
            tmp = {}
            for j in range(len(frame)):
                if frame[j] is not None:
                    v2 = frame[j]
                    tmp[j] = distance_measures.euclidean_distance( v1, v2 )
            min_dist_key = min(tmp, key=tmp.get)
            mappings[min_dist_key] = 1
        
        # Provide the set (non-dup) of nearest neighbour mappings to the frame.
        mapped = []
        for k in mappings.keys():
            mapped.append( frame[k] )
        
        return mapped

class Edge10MappedPositionEvaluator(VertexMappedPositionEvaluator, LoadEdgeFramePositions):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor) to the edges of the dome/ frame structure.
    
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model.
    Jan 2017.
    """
    def __init__(self, kwords):
        LoadLEDPositions.__init__(self)
        LoadEdgeFramePositions.__init__(self, kwords)  # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)

        self.leds_vertices = self.load_leds_positions()
        self.leds_vertices = self.map_to_frame( self.frame )
        self.shortname = "Mapped to dome edges ("+str(self.NUM_OF_VERTICES_PER_EDGE-1)+" points per edge. "+str(len(self.frame))+" total points)"





class VertexIndexPositionEvaluator(EvaluatorGeneric, LoadLEDIndexes, LoadFramePositions):
    """
    Load a set of dome index positions from a CSV results file, depending on column number. 
    Map those to indexes to vertices of the dome.
    Reevaluate those vertex positions and export a spreadsheet with lambertian illuminance scores per target surface.
    """
    def __init__(self, kwords={}):
        LoadLEDIndexes.__init__(self)
        LoadFramePositions.__init__(self, hardcoded_leds=kwords['all_leds'])
        leds_indexes = self.load_leds_indexes()
        self.frame = self.get_frame()

        self.leds_vertices = self.get_vertices_from_indexes(leds_indexes, self.frame)

        self.shortname = "LED Vertex Positions from Indexes."

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)

    def evaluate(self, triangles):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices)

    def tune( self, triangles ):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices)

class Edge10IndexPositionEvaluator(EvaluatorGeneric, LoadLEDIndexes, LoadEdgeFramePositions):
    """
    Load a set of dome EDGE index positions from a CSV results file, depending on column number.
    Load properties values in from properties file, under section ['EvaluateEdgeMapSingleResultsFile]'.
    Required: 3926 index positions. Produced by edges of 10 points.
    Map those indexes to vertices of the dome frame edges.
    Reevaluate those vertex positions and export a spreadsheet with lambertian illuminance scores per target surface.
    """
    def __init__(self, kwords):
        LoadLEDIndexes.__init__(self)
        LoadEdgeFramePositions.__init__(self, kwords)  # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
        leds_indexes = self.load_leds_indexes()
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)
        self.leds_vertices = self.get_vertices_from_indexes(leds_indexes, self.frame)
        self.shortname = "LED Edge Vertex Positions from Indexes."

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)

    def evaluate(self, triangles):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices)

    def tune(self, triangles):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices)








    # def load_selected_LED_indexes(self):
    #     dict_properties = getPropertiesFile("../properties/default.properties")
    #     csv_results_filename = dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.csvfilename']
    #     column_number = int(dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.column_number'])
    #     number_of_leds = int(dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.number_of_leds'])
    #     path_prefix = dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.results_output_file_path_prefix']
    #     source_filename = csv_results_filename
    #
    #     assert (os.path.exists(csv_results_filename))
    #     assert (column_number >= 0)
    #     assert (number_of_leds > 0 and number_of_leds <= 3991)
    #
    #     # Load the results file:
    #     best_LEDs = file_io.read_in_csv_file_to_list_of_lists(csv_results_filename, skip_header=False)
    #     # Get a list of the best index points:
    #     led_indexes = get_sorted_column_from_result_file(best_LEDs, column_index=column_number, qty=number_of_leds)
    #     return led_indexes, path_prefix, source_filename

    # def display(self, triangles, shape_name, kwords={}):
    #
    #     assert len(self.leds) > max(self.led_indexes), "Available quantity of LEDs ("+\
    #                               str(len(self.leds))+\
    #                               ") is less than the greatest index requested ("+str(max(self.led_indexes))+\
    #                               ")."
    #     for j in range(len(self.leds)):
    #         v = self.leds[j]
    #         draw_point( v, size=5 )
    #     for led_num in self.led_indexes:
    #         v = self.leds[led_num]
    #         draw_wire_sphere( vertex=v, size=2, scale=1 )
    #     for tri in triangles:
    #         make_triangle_face( tri )

    # def evaluate(self, triangles, shape_name, kwords={}):
    #     """
    #     Evaluate the standard deviation of lambertian illuminance of the terget shape, from the loaded leds vertex positions.
    #     """
    #     vertex_set = []
    #     for led_num in self.led_indexes:
    #         v = self.leds[led_num]
    #         vertex_set.append(v)
    #     surfaces = get_surface_evaluations(triangles, vertex_set)
    #     if are_all_surfaces_hit(surfaces) == False:
    #         print ("---FAILED--- to hit all surfaces. Result not written to file.")
    #     else:
    #         # extra_row_data = [self.shortname, self.objfilename, type(self).__name__]
    #         # row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces, self.leds,
    #         #                                                            filename_suffix="_single_edge10_result_file_evaluation",
    #         #                                                            path_prefix=self.path_prefix,
    #         #                                                            extra_row_data=extra_row_data)
    #
    #         extra_row_data = [self.shortname , self.objfilename, type(self).__name__]
    #         row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces,
    #                                                                    vertex_set, filename_suffix="_single-loaded-result-file-reevaluation",
    #                                                                    path_prefix=self.path_prefix,
    #                                                                    extra_row_data=extra_row_data)
    #         best_candidate_leds_index_set = self.leds
    #         print("Finished led vertex set:"+str(len(vertex_set))+", "+str(vertex_set))
    #         print("Finished led set:"+str(len(self.led_indexes))+", "+str(self.led_indexes))
    #         print("Finished result row:"+str(row))
    #         print("Finished with standard deviation:"+str(row[4]))
    #         print("Finished with normalised standard deviation:" + str(float(row[4]) / len(self.led_indexes)))
    #







