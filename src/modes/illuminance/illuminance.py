from __future__ import print_function
from __future__ import division
import sys

"""
    Illuminance Module:
    - Module containing algorithmic approaches that quantify based on amount of "light hitting the surface of a target object".
"""


currentMillis = lambda: int(round(time.time() * 1000))
from itertools import chain; flatten_x = lambda x: list(chain.from_iterable(x));

import logging
logging.basicConfig(format='%(message)s')

from datastructures.orderedset import ListHashableOrderedSet
from ..evaluator_generic import *
from .. import distance_measures
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
        self._lights_scale      = float(dict_properties['LightPositions']['light.scale'])
        self._path_prefix       = dict_properties['LightPositions']['light.results_output_file_path_prefix']
        self.shortname          = str(type(self).__name__)

    def load_leds_positions(self):
        # load in frame vertex positions as leds
        leds = read_vertices_objects( self._source_filename )[0]
        apply_scale( leds, scale=self._lights_scale )
        return leds

MEAN_INTENSITY = 0

class LoadLEDOutputIntensities(object):
    """
    Use this object as a mixin helper class to load in the LED lumens outputs (intensities), sorted by index values (from 0 to 'qty')
    Usage: 
    - In Constructor
        LoadLEDOutputIntensities.__init__(self)
        qty = len(led_vertices)
        self.intensities = self.load_led_intensities( qty )

    - In default.properties
        [LightOutput]
        light.output_intensity_from_index.column_number=(int, default=5, range=[0-99])
        light.output_intensity_from_index.filename_path=(string, path/to/file.csv)
        light.output_intensity_from_index.allow_default=(boolean, default=True)
        light.output_intensity_from_index.default_value=(float, default=1.0, range=[0.0-10.0])
    """
    def __init__(self):
        self._source_col_num = property_to_number(section="LightOutput", key="light.output_intensity_from_index.column_number", vmin=0, vmax=99, vtype=int)
        self._source_filename = property_to_string(section="LightOutput", key="light.output_intensity_from_index.filename_path")
        
        self._enforce_default = property_to_boolean(section="LightOutput", key="light.output_intensity_from_index.enforce_default")
        self._allow_default = property_to_boolean(section="LightOutput", key="light.output_intensity_from_index.allow_default")
        self._default_value = property_to_number(section="LightOutput", key="light.output_intensity_from_index.default_value", vmin=0.0, vmax=10.0, vtype=float)

    def load_led_intensities(self, quantity_of_leds):
        l = []
        if self._enforce_default:
            l = [self._default_value]*quantity_of_leds
        else:
            l = self.__load_led_intensities(quantity_of_leds)
        
        # l = 5 * np.random.random_sample(quantity_of_leds)
        #l = #[v-0.5 for v in l]
        set_once_key_value_pair(section="MEAN_INTENSITY", key="MEAN_INTENSITY", value=np.mean(l))
        return l

    def __load_led_intensities(self, quantity_of_leds):
        assert len(self._source_filename) != "", "Empty string for light.output_intensity_from_index.filename_path, cannot load intensities from file."
        assert type(quantity_of_leds) is int and quantity_of_leds > 0, "Entered quantity_of_leds for light.output_intensities is invalid or 0."

        l = read_column(self._source_filename, skip_header=False, column_num=self._source_col_num, quantity=quantity_of_leds)

        def __typecast_intensities(l):
            try:
                l = [float(v) for v in l]
            except ValueError as e:
                type_cast_succeeded = False
                assert type_cast_succeeded, "ValueError during typecast to float of loaded intensities values. In load_led_intensities(). Source data: "+str(l)
            return l
        
        def __validation(l, quantity_of_leds):
            incorrect_quantity_of_intensity_values  = not len(l) == quantity_of_leds
            incorrect_type_of_intensity_value       = not all([type(v) is float for v in l])
            if incorrect_quantity_of_intensity_values:
                print("Quantity of Light Intensity Values not equal to specified quantity")
                
            if incorrect_type_of_intensity_value:
                print("Validation warning: Light Intensity Value not of type float")

            if incorrect_quantity_of_intensity_values or incorrect_type_of_intensity_value:
                if self._allow_default:
                    has_valid_default_value = type(self._default_value) is float and self._default_value >= 0 and self._default_value <= 10.0
                    if has_valid_default_value:
                        print("Warning: applying default value for Light Intensity of "+str(self._default_value))
                        l = [self._default_value]*quantity_of_leds
                    else:
                        print("Invalid default value for Light Intensity of "+str(self._default_value)+" Cannot continue. Exiting.")
                        import sys; sys.exit()
                else:
                    print("Invalid Light Intensity Value data. Cannot continue. Exiting.")
                    import sys; sys.exit()
            else:
                # all is good
                pass
            return l

        l = __typecast_intensities(l)
        l = __validation(l, quantity_of_leds)
        return l


class LoadLEDIndexes(object):
    """
    Use this object as a mixin helper class to load in the LED index positions (to then later match with vertex positions).
    Usage: - In Constructor
        LoadLEDIndexes.__init__(self)
        self.leds = self.load_leds_indexes()
    """
    def __init__(self):
        dict_properties         = getPropertiesFile( "../properties/default.properties" )
        self._source_filename   = dict_properties['LightIndexPositions']['results_file.csvfilename']
        self._column_number     = int(dict_properties['LightIndexPositions']['results_file.column_number'])
        self._number_of_leds    = int(dict_properties['LightIndexPositions']['results_file.number_of_leds'])
        self._path_prefix       = dict_properties['LightIndexPositions']['results_file.results_output_file_path_prefix']
        self.shortname = str(type(self).__name__)

        assert (os.path.exists(self._source_filename))
        assert (self._column_number >= 0)
        assert (self._number_of_leds > 0)

    @staticmethod
    def get_vertices_from_indexes(indexes, vertices_list):
        led_vertices = []
        assert max(indexes) < len(vertices_list), "Requested position index(es) are out of the indexable frame position range.\n" \
                                                  "Maximum index: "+str(max(indexes))+"\n"\
                                                  "Maximum indexable position: "+str(len(vertices_list)-1)+"\n"\
                                                  "Maximum position quantity: "+str(len(vertices_list))+" (for arg: results_file.number_of_leds)"
        print("LED Indexes Length: "+str(len(indexes)))
        print("LED Source Vertices Length: "+str(len(vertices_list)))
        for i in indexes:
            if i >= len(vertices_list):
                logging.warn('Warning: request to select LED by an index value that is outside of the known set. %d / %d' % (i, len(vertices_list)))
            else:
                v = vertices_list[i]
                led_vertices.append( v ) if v is not None else None
                if v is None:
                    print("None Vertex for LED index: "+str(i))
        print("LED Final Vertices Length: "+str(len(led_vertices)))
        
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
    warned_frame_vertexes=False
    def __init__(self, hardcoded_leds=[]):
        dict_properties = getPropertiesFile("../properties/default.properties")
        self._frame_objfilename = dict_properties['FrameModel']['frame.objfilename']
        self._frame_scale = float(dict_properties['FrameModel']['frame.scale'])
        self.__hardcoded_leds = hardcoded_leds
        self.shortname = str(type(self).__name__)

        self._with_support_access = eval(dict_properties['FrameModel']['frame.withsupportaccess'])
        assert isinstance(self._with_support_access, bool), "[FrameModel] frame.withsupportaccess must be of type 'bool'. " \
                                                      "Found: "+str(type(self._with_support_access))

        self._frame_indexes_are_important = eval(dict_properties['FrameModel']['frame.indexes_are_important'])
        assert isinstance(self._frame_indexes_are_important, bool), "[FrameModel] frame.indexes_are_important must be of type 'bool'. " \
                                                              "Found: %s" % (str(type(self._frame_indexes_are_important)))
    
    def get_frame(self):
        if self._frame_indexes_are_important: # Hardcoded / not
            frame = self.get_hardcoded_frame()
        else:
            frame = self.__get_frame_from_obj()
        frame = self.__check_to_apply_support_access(frame)
        if not LoadFramePositions.warned_frame_vertexes:
            print("Frame has n mounting points available:"+str(len(frame)))
            LoadFramePositions.warned_frame_vertexes=True
        return frame

    def get_hardcoded_frame(self):
        assert self.__hardcoded_leds is not None and len(self.__hardcoded_leds) > 0, \
                                                    "Number of hardcoded LEDs should be GT 0."
        return self.__hardcoded_leds

    def get_file_loaded_frame(self):
        return self.__get_frame_from_obj()

    def __get_frame_from_obj(self):
        # load in frame vertex positions as leds
        frame = read_vertices_objects(self._frame_objfilename)[0]
        apply_scale(frame, scale=self._frame_scale)
        assert len(frame) > 0, "Frame loaded from .obj file %s" % (str(self._frame_objfilename))
        return frame

    def __check_to_apply_support_access(self, frame):
        if self._with_support_access:
            n = property_to_number(section="FrameModel", key="frame.support_access_vertices_to_remove", vmin=1, vmax=15, vtype=int)
            frame = self.__remove_bottom_most_n_LED_vertices( frame, n )
        return frame

    def __remove_bottom_most_n_LED_vertices(self, frame, n=1):
        assert frame is not None and len(frame) > 0, "Number of frame LED positions should be GT 0."
        # Only remove if not yet removed. i.e... all([[1,2],[3,4]]) == True .... alternatively:  all([[1,2],None]) == False
        if all(frame):
            y_axis = [y for [x, y, z] in frame]
            removed = []
            # Loop, replacing the lowest y-axis index with none
            for i in range(n):
                lowest_y         = y_axis.index(min(y_axis))
                y_axis[lowest_y] = sys.maxint
                frame[lowest_y]  = None
                removed.append(lowest_y)
            
        print( "Support Access: Number of Remaining Frame vertices: " +str(len(frame)-frame.count(None))+"\tRemoved LED indexes: "+str(removed))
        return frame


class LoadEdgeFramePositions(LoadFramePositions):
    """
    Use this object as a mixin helper class to load in the LED frame and split each frame edge into 10 vertex positions.
    Usage: - In Constructor
        LoadEdgeFramePositions.__init__(self, kwords, NUM_OF_VERTICES_PER_EDGE=11)   
                                                # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
                                                # NUM_OF_VERTICES_PER_EDGE -- This number should include the start vertex and end vertex of the edge, as well as the new vertex points along the edge.
                                                                           -- Default is '11' for 10 points per edge. Calculated as each edge having 8 new points, plus the start and end vertices. 
                                                                           -- Depends on Range(a,b) function where (b) is exclusive. Use '3' for 1 additional point in each edge's centre.
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)
    """
    warned_frame_vertexes=False
    def __init__(self, kwords, NUM_OF_VERTICES_PER_EDGE=11):
        LoadFramePositions.__init__(self, hardcoded_leds=kwords['all_leds'])
        self.NUM_OF_VERTICES_PER_EDGE = NUM_OF_VERTICES_PER_EDGE  # --  This number should include the start vertex and end vertex of the edge, as well as the new vertex points along the edge.
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
        unique_vertex_dict = {}
        vertex_index_edge_divided_already_dict = {}
        absZeroes = lambda x: 0 if x == -0 else x
        myTruncate = lambda y: [float('%.3f'%(absZeroes(x))) for x in y]

        assert len(faces) > 0, "The number of faces loaded from the OBJ model file specified in [FrameModel] must be GT 0."
        assert isinstance(faces, list), "Faces data expected as iterable. Found: " + str(type(faces))

        # For all faces, we will get the new set of vertices, including existing and the newly calculated vertices that
        # resulted from the edge segmenting
        for poly_face in faces:
            # - Example of a face triple:
            # frame[poly_face[0]] == [2.611816, 7.513872, -0.848632]
            # frame[poly_face[1]] == [0.0, 7.513872, -2.746232]
            # frame[poly_face[2]] == [-2.611816, 7.513872, -0.848632]
            # frame[poly_face[3]] == [-2.611816, 7.513872, -0.848632]

            # Each edge of the face is connected as follows:
            def _get_edge_pairs( l ):
                """
                >>> o = [[x,x+1] for x in range(len(l))]
                >>> o[len(o)-1][1] = 0
                >>> o
                [[0, 1], [1, 2], [2, 0]]
                """
                o = [[x,x+1] for x in range(len(l))]
                o[len(o)-1][1] = 0  # Wrap final edge's pair back to 0.
                return o
            edges = _get_edge_pairs( poly_face )

            # If any point on the current face doesn't have a corresponding vertex position, then abort this face.
            if not all([frame[t - 1] is not None for t in poly_face]):
                continue

            # For all of the edges of this face:
            for edge in edges:

                # start and end of line:
                v1_from = frame[poly_face[edge[0]] - 1]
                v2_to = frame[poly_face[edge[1]] - 1]

                # Ensure removal of duplicates in EDGE-Vertex-Index combinations:
                def has_vertex_index_edge_set_divided_already():
                    edge_divided_already = False
                    # Specify the key, in either order:
                    make_ind_key = lambda a, b:  str(str( a ) +":"+ str( b ))
                    forw_ind_key = make_ind_key( poly_face[edge[0]] - 1, poly_face[edge[1]] - 1 )
                    back_ind_key = make_ind_key( poly_face[edge[1]] - 1, poly_face[edge[0]] - 1 )

                    if forw_ind_key in vertex_index_edge_divided_already_dict:
                        edge_divided_already = True
                    else:
                        vertex_index_edge_divided_already_dict[ forw_ind_key ] = 1
                        vertex_index_edge_divided_already_dict[ back_ind_key ] = 1
                    return edge_divided_already

                if has_vertex_index_edge_set_divided_already():
                    continue

                # translate to the first point of line:
                v1_start = [0, 0, 0]
                v2_end = [v2_to[0] - v1_from[0], v2_to[1] - v1_from[1], v2_to[2] - v1_from[2]]
                local_vertices = []

                is_Edge1        = self.NUM_OF_VERTICES_PER_EDGE - 1 == 1
                is_GTEQ_Edge2   = self.NUM_OF_VERTICES_PER_EDGE - 1 > 1
                if is_Edge1:
                    # calculate the fixed mid-point along the line (excluding start- and end-points)
                    v2_unit = [x / 2 for x in v2_end]
                    # Only add the unit vertex. Ignore start and end vertices of this edge.
                    local_vertices.append(v2_unit)
                elif is_GTEQ_Edge2:
                    # calculate the first point along the line (excluding start- and end-points)
                    v2_unit = [x / (self.NUM_OF_VERTICES_PER_EDGE - 1) for x in v2_end]
                    # Divide line by 10. Create a new vertex at (l/10)*1, (l/10)*2, (l/10)*3, .. (l/10)*9,
                    for d in range(0, self.NUM_OF_VERTICES_PER_EDGE): # -- Note: Range(a,b) is inclusive (a) and exclusive (b).
                        v = [x * d for x in v2_unit]
                        local_vertices.append(v)

                # translate all new local coordinates back into global space, push them onto the ordered set of vertices.
                for i in range(len(local_vertices)):
                    v = local_vertices[i]
                    gv = [v[0] + v1_from[0], v[1] + v1_from[1], v[2] + v1_from[2]]

                    # Ensure removal of duplicates in matching resultant Global VERTEX positions, to 6s.f.:
                    if str(myTruncate(gv)) in unique_vertex_dict:
                        continue
                    unique_vertex_dict[ str(myTruncate(gv)) ] = 1
                    global_vertices.add(gv)

        # Transfer into new list object to return.
        return_frame = list(global_vertices)

        if not LoadEdgeFramePositions.warned_frame_vertexes:
            print("Edge-divided Frame has n mounting points available:"+str(len(return_frame)))
            LoadEdgeFramePositions.warned_frame_vertexes=True
        return return_frame


class RawPositionEvaluator(EvaluatorGeneric, LoadLEDPositions, LoadFramePositions, LoadLEDOutputIntensities):
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

        LoadLEDOutputIntensities.__init__(self)
        qty = len(self.leds_vertices)
        self.intensities = self.load_led_intensities( qty )

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)
            
    def evaluate( self, triangles ):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices, self.intensities)

    def tune( self, triangles ):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices, self.intensities)


class VertexMappedPositionEvaluator(RawPositionEvaluator):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor)
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model, using a specified set of light vertex positions, i.e. Lettvin's diffuse positions.
    Jan 2017.
    """
    def __init__(self, kwords):
        RawPositionEvaluator.__init__(self, kwords)
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


class Wrapper_EdgeXMappedPositionEvaluator(VertexMappedPositionEvaluator, LoadEdgeFramePositions):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor) to the edges of the dome/ frame structure.
    
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model.
    Jan 2017.
    """
    def __init__(self, kwords, NUM_OF_VERTICES_PER_EDGE):
        RawPositionEvaluator.__init__(self, kwords)
        LoadLEDPositions.__init__(self)
        LoadEdgeFramePositions.__init__(self, kwords, NUM_OF_VERTICES_PER_EDGE)  # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)

        self.leds_vertices = self.load_leds_positions()
        self.leds_vertices = self.map_to_frame( self.frame )
        self.shortname = "Mapped to dome edges ("+str(self.NUM_OF_VERTICES_PER_EDGE-1)+" points per edge. "+str(len(self.frame))+" total points)"

class EdgeXMappedPositionEvaluator(Wrapper_EdgeXMappedPositionEvaluator):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor) to the edges of the dome/ frame structure.
    
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model.
    Jan 2017.
    """
    def __init__(self, kwords):
        q = property_to_number(section="FrameModel", key="frame.number_of_vertices_per_edge", vmin=1, vmax=10, vtype=int)
        Wrapper_EdgeXMappedPositionEvaluator.__init__(self, kwords, NUM_OF_VERTICES_PER_EDGE=q+1 if q is not None else 3)

class VertexIndexPositionEvaluator(EvaluatorGeneric, LoadLEDIndexes, LoadFramePositions, LoadLEDOutputIntensities):
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

        LoadLEDOutputIntensities.__init__(self)
        qty = len(self.leds_vertices)
        self.intensities = self.load_led_intensities( qty )

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)

    def evaluate(self, triangles):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices, self.intensities)

    def tune( self, triangles ):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices, self.intensities)

class Wrapped_EdgeXIndexPositionEvaluator(EvaluatorGeneric, LoadLEDIndexes, LoadEdgeFramePositions, LoadLEDOutputIntensities):
    """
    Load a set of dome EDGE index positions from a CSV results file, depending on column number.
    Load properties values in from properties file, under section ['EvaluateEdgeMapSingleResultsFile]'.
    Required: is `(270*(X-1))+92` index positions. Produced by edges with EdgeX-1 additional points.
    Map those indexes to vertices of the dome frame edges.
    Reevaluate those vertex positions and export a spreadsheet with lambertian illuminance scores per target surface.
    """
    def __init__(self, kwords, NUM_OF_VERTICES_PER_EDGE=None):
        LoadLEDIndexes.__init__(self)
        LoadEdgeFramePositions.__init__(self, kwords, NUM_OF_VERTICES_PER_EDGE)  # kwords['all_leds'] = [] -- should contain the hardcoded frame vertex positions.
        leds_indexes = self.load_leds_indexes()
        self.frame = self.get_frame()
        self.frame = self.get_frame_edge_points(self.frame)
        self.leds_vertices = self.get_vertices_from_indexes(leds_indexes, self.frame)
        self.shortname = "LED Edge"+str(NUM_OF_VERTICES_PER_EDGE-1)+" Vertex Positions from Indexes."

        LoadLEDOutputIntensities.__init__(self)
        qty = len(self.leds_vertices)
        self.intensities = self.load_led_intensities( qty )

    def display(self, triangles):
        EvaluatorGeneric.display(self, triangles, self.frame, self.leds_vertices)

    def evaluate(self, triangles):
        EvaluatorGeneric.evaluate(self, triangles, self.leds_vertices, self.intensities)

    def tune(self, triangles):
        EvaluatorGeneric.tune(self, triangles, self.leds_vertices, self.intensities)



class EdgeXIndexPositionEvaluator(Wrapped_EdgeXIndexPositionEvaluator):
    """
    Wrapper for EdgeXIndexPositionEvaluator class, with Edge argument value specified by the properties file source data.
    """
    def __init__(self, kwords): 
        q = property_to_number(section="FrameModel", key="frame.number_of_vertices_per_edge", vmin=1, vmax=10, vtype=int)
        Wrapped_EdgeXIndexPositionEvaluator.__init__(self, kwords, NUM_OF_VERTICES_PER_EDGE=q+1 if q is not None else 3)

