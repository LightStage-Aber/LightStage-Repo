"""
    Illuminance Module:
    - Module containing algorithmic approaches that quantify based on amount of "light hitting the surface of a target object".
"""

from __future__ import division
import random as rnd
import time;     currentMillis = lambda: int(round(time.time() * 1000))
import os

import logging
logging.basicConfig(format='%(message)s')

from datastructures.orderedset import OrderedSet, ListHashableOrderedSet
from options import *
from file_utils import *
from model_helpers.stats_helper import iqr
from data_3d.obj_model_reader import get_all_vertex_face_objects, apply_scale
from ..manipulate_results_data import *
from ..visualisations import *
from ..evaluations import Evaluator
from .. import distance_measures
import monte_carlo_sequences

class MeasureLoadedLightPositions(Evaluator):
    """
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model, using a specified set of light vertex positions, i.e. Lettvin's diffuse positions.
    Jan 2017.
    """
    def __init__(self):
        super(MeasureLoadedLightPositions, self).__init__()
        self.leds, self.path_prefix, self.objfilename = self.load_leds()
        self.shortname = "Raw Lettvin Positions"
        
    def load_leds(self):
        # load in frame vertex positions as leds
        dict_properties         = getPropertiesFile( "../properties/default.properties" )
        lights_sourcefilename   = dict_properties['LightPositions']['light.objfilename']
        lights_scale            = float(dict_properties['LightPositions']['light.scale'])
        path_prefix             = dict_properties['LightPositions']['light.results_output_file_path_prefix']
        leds = read_vertices_objects( lights_sourcefilename )[0]
        apply_scale( leds, scale=lights_scale )
        return leds, path_prefix, lights_sourcefilename
    
    def display(self, triangles, shape_name, kwords={} ):
        """
        Draw the target shape and light vertex positions.
        """
        for i in range(kwords['QTY_OF_BEST_LEDS_REQUIRED']):
            led = self.leds[i]
            draw_wire_sphere( vertex=led, size=0.1, scale=1 )
        for tri in triangles:
            make_triangle_face( tri )
            
    def evaluate( self, triangles, shape_name, kwords={} ):
        """
        Evaluate the standard deviation of lambertian illuminance of the terget shape, from the loaded leds vertex positions.
        """
        #self.display(triangles, shape_name, kwords )
        #return
        surfaces = get_surface_evaluations(triangles, self.leds)
        if are_all_surfaces_hit(surfaces) == False:
            print "---FAILED--- to hit all surfaces. Result not written to file."
        else:
            extra_row_data = [self.shortname , self.objfilename, type(self).__name__]
            row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces, self.leds, filename_suffix="_lettvin_evaluation", path_prefix=self.path_prefix, extra_row_data=extra_row_data)
            best_candidate_leds_index_set = self.leds
            #write_led_result_file(self.leds, best_candidate_leds_index_set)
            print "Finished with standard deviation:"+str(row[2])
            print "Finished with Num of LEDS: "+str(len(best_candidate_leds_index_set))
        sys.exit()


class MeasureMappingOfLoadedLightPositions(MeasureLoadedLightPositions):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor)
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model, using a specified set of light vertex positions, i.e. Lettvin's diffuse positions.
    Jan 2017.
    """
    def __init__(self):
        super(MeasureMappingOfLoadedLightPositions, self).__init__()    #call super
        self.frame = self.get_frame() 
        self.frame = self.remove_bottom_LED_vertex( self.frame )
        self.mapped = self.map_to_frame( self.frame )
        self.shortname = "Mapped to dome vertices ("+str(len(self.frame))+" points)"
    def get_frame(self):
        # load in frame vertex positions as leds
        dict_properties         = getPropertiesFile( "../properties/default.properties" )
        frame_sourcefilename    = dict_properties['FrameModel']['frame.objfilename']
        frame_scale             = float(dict_properties['FrameModel']['frame.scale'])
        
        frame = read_vertices_objects( frame_sourcefilename )[0]
        apply_scale( frame, scale=frame_scale )
        
        return frame
        
    def remove_bottom_LED_vertex(self, frame):
        #self.frame = kwords['all_leds']
        y_axis = [y for [x,y,z] in frame]
        lowest_y = y_axis.index(min(y_axis))
        del(frame[lowest_y])
        return frame
        
    def map_to_frame(self, frame):
        
        mappings = {}
        for v1 in self.leds:
            tmp = {}
            for j in range(len(frame)):
                v2 = frame[j]
                tmp[j] = distance_measures.euclidean_distance( v1, v2 )
            min_dist_key = min(tmp, key=tmp.get)
            mappings[min_dist_key] = 1
        
        # Provide the set (non-dup) of nearest neighbour mappings to the frame.
        mapped = []
        for k in mappings.keys():
            mapped.append( frame[k] )
        
        return mapped
        
    def display(self, triangles, shape_name, kwords={} ):
        """
        Draw the target shape and light vertex positions.
        """
#        for i in range(len(self.leds)): # range(kwords['QTY_OF_BEST_LEDS_REQUIRED']):
#            led = self.leds[i]
#            draw_wire_sphere( vertex=led, size=0.1, scale=1 )
#        for j in range(len(self.frame)):
#            led = self.frame[j]
#            draw_point( led, size=8 )
        for m in self.mapped:
            draw_solid_sphere( vertex=m, size=2, scale=1 )
#        for tri in triangles:
#            make_triangle_face( tri )
   
   
    def evaluate( self, triangles, shape_name, kwords={} ):
        """
        Evaluate the standard deviation of lambertian illuminance of the terget shape, from the mapped leds vertex positions.
        """
        surfaces = get_surface_evaluations(triangles, self.mapped)
        if are_all_surfaces_hit(surfaces) == False:
            print "---FAILED--- to hit all surfaces. Result not written to file."
        else:
            extra_row_data = [self.shortname , self.objfilename, type(self).__name__]
            row = write_led_set_lambertian_scores_appended_result_file(self.mapped, surfaces, self.mapped, filename_suffix="_lettvin_evaluation", path_prefix=self.path_prefix, extra_row_data=extra_row_data)
            best_candidate_leds_index_set = self.mapped
            #write_led_result_file(self.mapped, best_candidate_leds_index_set)
            print "Finished with standard deviation: "+str(row[2])
            print "Finished with Num of LEDS: "+str(len(best_candidate_leds_index_set))
        sys.exit()


class MeasureMappingToEdgesOfLoadedLightPositions(MeasureMappingOfLoadedLightPositions):
    """
    Map the specified set of light vertex positions (loaded in the super class constructor) to the edges of the dome/ frame structure.
    
    Evaluate the standard deviation of lambertian illuminance on surfaces of a target model.
    Jan 2017.
    """
    def __init__(self):
        super(MeasureMappingOfLoadedLightPositions, self).__init__()    #call super
        self.NUM_OF_VERTICES_PER_EDGE = 11 # --  This number should include the start vertex and end vertex of the edge, as well as the new vertex points along the edge.
        assert( self.NUM_OF_VERTICES_PER_EDGE > 0 )
        self.frame = self.get_frame()
        self.frame = self.remove_bottom_LED_vertex( self.frame )
        self.frame = self.get_frame_edge_points( self.frame )
        self.mapped = self.map_to_frame( self.frame )
        self.shortname = "Mapped to dome edges ("+str(self.NUM_OF_VERTICES_PER_EDGE-1)+" points per edge. "+str(len(self.frame))+" total points)"
    
    def get_frame_edge_points(self, frame):
        dict_properties = getPropertiesFile( "../properties/default.properties" )
        frame_sourcefilename = dict_properties['FrameModel']['frame.objfilename']
        global_vertices = ListHashableOrderedSet()  # Push each new vertex point into an OrderedSet, to avoid duplicate vertices due to edges starting/ending at matching points and to avoid duplicate points along the two edges with the same start/end vertex points (i.e. the edges of two adjacent triangles).

        # Get edges between vertices, in order to segment each edge into n vertices.
        faces = read_faces_objects( frame_sourcefilename )[0]
        assert( len(faces) > 0 )
        
        # Get new vertices, including existing and the newly calculated vertices that resulted from the edge segmenting.
        for triple in faces:
            # - Example of a face triple:
            # frame[triple[0]] == [2.611816, 7.513872, -0.848632]
            # frame[triple[1]] == [0.0, 7.513872, -2.746232]
            # frame[triple[2]] == [-2.611816, 7.513872, -0.848632]
            edges = [(0,1),(1,2),(2,0)] 
            
            for edge in edges:
                # Check if position is valid:
                if not self.is_valid_edge_vertices(frame, edge, triple):
                    continue
                # start and end of line:
                v1_from = frame[triple[edge[0]]-1] 
                v2_to   = frame[triple[edge[1]]-1]
                
                # translate to the first point of line:
                v1_start = [0,0,0]
                v2_end   = [ v2_to[0]-v1_from[0], v2_to[1]-v1_from[1], v2_to[2]-v1_from[2] ]
                local_vertices = []
                
                # calculate the first point along the line (excluding start- and end-points)
                v2_unit = [x/(self.NUM_OF_VERTICES_PER_EDGE-1) for x in v2_end]

                # Divide line by 10. Create a new vertex at (l/10)*1, (l/10)*2, (l/10)*3, .. (l/10)*9, 
                for d in range(0,self.NUM_OF_VERTICES_PER_EDGE):
                    v = [x*d for x in v2_unit]
                    local_vertices.append( v )                
                
                # translate all new local coordinates back into global space, push them onto the ordered set of vertices.
                for i in range(len(local_vertices)):
                    v   = local_vertices[i]
                    gv  = [ v[0]+v1_from[0] , v[1]+v1_from[1] , v[2]+v1_from[2] ]
                    global_vertices.add( gv )
            
        # Transfer into new list object to return.
        return_frame = list(global_vertices)        
        
        return return_frame
        
    def is_valid_edge_vertices(self, frame, edge, triple):
        i = None
        for e in edge:
            if triple[e]-1 >= len(frame):
                i = e
        #if i != None:
            #print("Ignoring frame vertex: "+str(triple[i]-1))        
        return i == None


# -----------------------------------------------------------
class MeasureIlluminanceOfResultsFileSet_MappingToDomeVertices( Evaluator ):
    """
    Load a set of dome index positions from a CSV results file, depending on column number. 
    Map those to indexes to vertices of the dome.
    Reevaluate those vertex positions and export a spreadsheet with lambertian illuminance scores per target surface.
    """
    
    def __init__(self):
        super(Evaluator, self).__init__()    #call super
        self.led_indexes, self.path_prefix, self.source_filename = self.load_selected_LED_indexes()
        self.shortname = "Reevaluation based on LED indexes from result file."
        
    def load_selected_LED_indexes(self):
        dict_properties                 = getPropertiesFile( "../properties/default.properties" )
        csv_results_filename            = dict_properties['EvaluateSingleResultsFile']['results_file.csvfilename']
        column_number                   = int(dict_properties['EvaluateSingleResultsFile']['results_file.column_number'])
        number_of_leds                  = int(dict_properties['EvaluateSingleResultsFile']['results_file.number_of_leds'])
        path_prefix                     = dict_properties['EvaluateSingleResultsFile']['results_file.results_output_file_path_prefix']
        source_filename                 = csv_results_filename
        
        
        assert( os.path.exists(csv_results_filename) )
        assert( column_number >= 0 )
        assert( number_of_leds > 0 and number_of_leds <= 92 )
        
        # Load the results file:
        best_LEDs       = file_io.read_in_csv_file_to_list_of_lists(csv_results_filename, skip_header=False)
        # Get a list of the best index points:
        led_indexes     = get_sorted_column_from_result_file( best_LEDs, column_index=column_number, qty=number_of_leds )
        return led_indexes, path_prefix, source_filename
        
    def display( self, triangles, shape_name, kwords={} ):
        """
        Draw the target shape and light vertex positions.
        """
        for j in range(len(kwords['all_leds'])):
            v = kwords['all_leds'][j]
            draw_point( v, size=8 )
        for led_num in self.led_indexes:
            v = kwords['all_leds'][led_num]
            draw_wire_sphere( vertex=v, size=2, scale=1 )
        for tri in triangles:
            make_triangle_face( tri )
            
    def evaluate( self, triangles, shape_name, kwords={} ):
        self.leds       = self.get_leds(kwords)
        # Get dome vertices corresponding to the loaded index points:
        led_vertex_set = []
        for led_num in self.led_indexes:
            if led_num >= len(self.leds):
                logging.warn('Warning: request to select LED by an index value that is outside of the known set.')
            else:
                led_vertex_set.append( self.leds[led_num] )

        #print(led_vertex_set)
        surfaces    =  get_surface_evaluations(triangles, led_vertex_set)
        if are_all_surfaces_hit(surfaces) == False:
            print("Finished led set:"+str(self.led_indexes))
            print("---FAILED--- to hit all surfaces. Result not written to file.")
        else:
            extra_row_data = [self.shortname , self.source_filename, type(self).__name__]
            row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces, led_vertex_set, filename_suffix="_single-loaded-result-file-reevaluation", path_prefix=self.path_prefix, extra_row_data=extra_row_data)
            #best_candidate_leds_index_set = self.led_indexes
            #write_led_result_file(all_leds, best_candidate_leds_index_set)
            print("Finished led vertex set:"+str(len(led_vertex_set))+", "+str(led_vertex_set))
            print("Finished led set:"+str(len(self.led_indexes))+", "+str(self.led_indexes))
            print("Finished result row:"+str(row))
            print("Finished with standard deviation:"+str(row[4]))
        sys.exit()
    def get_leds(self, kwords={}):
        # Get all dome vertices:
        all_leds = []
        dict_properties = getPropertiesFile( "../properties/default.properties" )
        use_hardcoded   = dict_properties['EvaluateSingleResultsFile']['results_file.use_hardcoded_dome_frame_vertices']
        if use_hardcoded not in ["True", "False"]:
            raise("Invalid Property in default.properties at '[EvaluateSingleResultsFile]->results_file.use_hardcoded_dome_frame_vertices'. Must be 'True' (to use hard coded dome frame) or 'False' (to use .obj file addressed by [FrameModel]->'frame.objfilename').")
        else:
            if eval(use_hardcoded) == True:
                all_leds                = kwords['all_leds']
            else:
                frame_scale             = float(dict_properties['FrameModel']['frame.scale'])
                frame_sourcefilename    = dict_properties['FrameModel']['frame.objfilename']
                leds                    = read_vertices_objects( frame_sourcefilename )[0]
                apply_scale( leds, scale=frame_scale )
                all_leds                = leds
        return all_leds
        

class MeasureIlluminanceOfResultsFileSet_MappingToDomeEdges( MeasureIlluminanceOfResultsFileSet_MappingToDomeVertices ):
    """
    Load a set of dome EDGE index positions from a CSV results file, depending on column number.
    Load properties values in from properties file, under section ['EvaluateEdgeMapSingleResultsFile]'.
    Required: 3926 index positions. Produced by edges of 10 points.
    Map those indexes to vertices of the dome frame edges.
    Reevaluate those vertex positions and export a spreadsheet with lambertian illuminance scores per target surface.
    """
    def __init__(self):
        super(Evaluator, self).__init__()  # call super
        self.led_indexes, self.path_prefix, self.objfilename = self.load_selected_LED_indexes()
        self.shortname = "Reevaluation based on LED indexes to dome edges from result file."
        x = MeasureMappingToEdgesOfLoadedLightPositions()
        frame = x.get_frame()
        frame = x.remove_bottom_LED_vertex( frame )
        self.leds = x.get_frame_edge_points( frame )


    def load_selected_LED_indexes(self):
        dict_properties = getPropertiesFile("../properties/default.properties")
        csv_results_filename = dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.csvfilename']
        column_number = int(dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.column_number'])
        number_of_leds = int(dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.number_of_leds'])
        path_prefix = dict_properties['EvaluateEdgeMapSingleResultsFile']['edge_results_file.results_output_file_path_prefix']
        source_filename = csv_results_filename

        assert (os.path.exists(csv_results_filename))
        assert (column_number >= 0)
        assert (number_of_leds > 0 and number_of_leds <= 3991)

        # Load the results file:
        best_LEDs = file_io.read_in_csv_file_to_list_of_lists(csv_results_filename, skip_header=False)
        # Get a list of the best index points:
        led_indexes = get_sorted_column_from_result_file(best_LEDs, column_index=column_number, qty=number_of_leds)
        return led_indexes, path_prefix, source_filename

    def display(self, triangles, shape_name, kwords={}):
        for j in range(len(self.leds)):
            v = self.leds[j]
            draw_point( v, size=8 )
        for led_num in self.led_indexes:
            v = self.leds[led_num]
            draw_wire_sphere( vertex=v, size=2, scale=1 )
        for tri in triangles:
            make_triangle_face( tri )

    def evaluate(self, triangles, shape_name, kwords={}):
        """
        Evaluate the standard deviation of lambertian illuminance of the terget shape, from the loaded leds vertex positions.
        """
        vertex_set = []
        for led_num in self.led_indexes:
            v = self.leds[led_num]
            vertex_set.append(v)
        surfaces = get_surface_evaluations(triangles, vertex_set)
        if are_all_surfaces_hit(surfaces) == False:
            print "---FAILED--- to hit all surfaces. Result not written to file."
        else:
            # extra_row_data = [self.shortname, self.objfilename, type(self).__name__]
            # row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces, self.leds,
            #                                                            filename_suffix="_single_edge10_result_file_evaluation",
            #                                                            path_prefix=self.path_prefix,
            #                                                            extra_row_data=extra_row_data)

            extra_row_data = [self.shortname , self.objfilename, type(self).__name__]
            row = write_led_set_lambertian_scores_appended_result_file(self.leds, surfaces,
                                                                       vertex_set, filename_suffix="_single-loaded-result-file-reevaluation",
                                                                       path_prefix=self.path_prefix,
                                                                       extra_row_data=extra_row_data)
            best_candidate_leds_index_set = self.leds
            print("Finished led vertex set:"+str(len(vertex_set))+", "+str(vertex_set))
            print("Finished led set:"+str(len(self.led_indexes))+", "+str(self.led_indexes))
            print("Finished result row:"+str(row))
            print("Finished with standard deviation:"+str(row[4]))
        sys.exit()


''' AOS TEST
# -----------------------------------------------------------
def evaluate_illuminance_score_result_file_set_tune_weights( updateable_line, camerasVertices, triangles, shape_name ):
    global cameraPos, scale, logged_score_to_file, loggable    
    
    best_LEDs        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
    led_index_set    = get_sorted_column_from_result_file( best_LEDs, CSV_METRIC_COLUMN_INDEX=3, QTY_OF_BEST_LEDS_REQUIRED=44 )
    
    all_leds        = draw_dome( scale , True )
    
    print len(led_index_set)
    led_vertex_weights = np.ones(len(all_leds))
 
    faces = dome_obj_data.get_dome_edges()

    led_vertex_set = []
    for led_num in led_index_set:
        led_vertex_set.append( all_leds[led_num] )
    # aos test
    print 'RUNNING FULL LAMBERTIAN EVALS'
    multi_surfaces    =  get_full_set_surface_evaluations(triangles, all_leds)
    #print(multi_surfaces)

    # try to smooth the surface variations
    for i in range(1000):

      #sum the lambertian scores from each led that is selected
      lam_scores = np.zeros(len(triangles));
      for led_num in led_index_set:
	for t in range(len(triangles)):
	    lam_scores[t] += multi_surfaces[led_num,t] * led_vertex_weights[led_num]

      #get the mean value and find the face furthest from the mean
      mean = np.mean(lam_scores)
      worst_face=0
      worst_face_delta=0
      for t in range(len(triangles)):
        delta = np.absolute(lam_scores[t] - mean)
        if ( delta > worst_face_delta):
          worst_face_delta = delta
          worst_face = t

      # process the 3 vertices on the worst face
      delta = mean - lam_scores[worst_face] 

      vertices = faces[worst_face]
      #for vertex in range (1,4):
	#print vertices[vertex] - 1
      #  led_vertex_weights[vertices[vertex] -1] += 0.01 * np.sign(delta)

      max = 0
      max_led=0
      for led_num in led_index_set:
        if(multi_surfaces[led_num,worst_face] > max):
          if(led_vertex_weights[led_num] > 0.6):
            max = multi_surfaces[led_num,worst_face]
            max_led = led_num

      led_vertex_weights[max_led] += 0.01* np.sign(delta)

      #print lam_scores
      print np.std(lam_scores)
      print np.mean(lam_scores)
      print worst_face_delta
      print worst_face
      # end aos test
     
    print led_vertex_weights
    sys.exit()
'''






# PDS7 REFACTORING
class MeasureIlluminanceTuneWeights_AOS( Evaluator ):
    def evaluate( self, updateable_line, camerasVertices, triangles, shape_name ):
        global cameraPos, scale, logged_score_to_file, loggable    
        
        best_LEDs        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
        led_index_set    = get_sorted_column_from_result_file( best_LEDs, CSV_METRIC_COLUMN_INDEX=3, QTY_OF_BEST_LEDS_REQUIRED=44 )
        
        all_leds        = draw_dome( scale , True )
        
        print len(led_index_set)
        print led_index_set

        led_vertex_weights = np.zeros(len(all_leds))
     
        for led in led_index_set:
          #print led
          led_vertex_weights[led] = 1.0

        faces = dome_obj_data.get_dome_edges()

        led_vertex_set = []
        for led_num in led_index_set:
            led_vertex_set.append( all_leds[led_num] )
        # aos test
        print 'RUNNING LED WEIGHT EVALS'
        multi_surfaces    =  get_full_set_surface_evaluations(triangles, all_leds)
        #print(multi_surfaces)

        best_weighting = np.copy(led_vertex_weights)
        best_std_dev = 10000

        # try to smooth the surface variations
        for i in range(1000):

          #sum the lambertian scores from each led that is selected
          lam_scores = np.zeros(len(triangles));
          for led_num in led_index_set:
	    for t in range(len(triangles)):
	        lam_scores[t] += multi_surfaces[led_num,t] * led_vertex_weights[led_num]


          dev = np.std(lam_scores)
          if(dev < best_std_dev):
	    best_std_dev = dev
            best_weighting = np.copy(led_vertex_weights)
          else:
            led_vertex_weights = np.copy(best_weighting)

          rand = rnd.randint(0,len(all_leds)/2)
          led_vertex_weights[rand] -=0.01
          led_vertex_weights[91 - rand] -=0.01


          #print lam_scores
          print np.std(lam_scores)
    #      print np.mean(lam_scores)
          # end aos test
         
        print best_weighting
        sys.exit()




''' 
# -----------------------------------------------------------
def evaluate_illuminance_score_multiple_result_file_set( updateable_line, camerasVertices, triangles, shape_name , count, kwords):
    """ 
    Based on an initial set of LED positions. 
    Randomly swap-in/out 1 from top-half and 1 from bottom-half of dome. 
    Continue until the count is exceeded. 
    Measure standard deviation of suface illuminance, whlie measuring lambertian score from current LED set.
    Report lowest standard deviation score and its LED index set.
    """
    global cameraPos, scale, logged_score_to_file, loggable    
    
    
    
    best_LEDs        = file_io.read_in_csv_file_to_list_of_lists( kwords['LED_SCORE_LOG_FILE'], skip_header=False )
    led_index_set    = get_sorted_column_from_result_file( 	best_LEDs, 
    														kwords['CSV_METRIC_COLUMN_INDEX'], 
    														kwords['QTY_OF_BEST_LEDS_REQUIRED'] 
    														)
    
    

    # store the active leds
    selected_leds = np.zeros(len(kwords['all_leds']))
    for led_num in led_index_set:
        selected_leds[led_num] = 1

    multi_surfaces    =  get_full_set_surface_evaluations(triangles, kwords['all_leds'])

    best_stddev = 100

    for i in range(count):
        #sum the lambertian scores from each led that is selected
        num_tri = len(triangles);
        lam_scores = np.zeros(num_tri);
        for led_num in range (len(selected_leds)):
            if(selected_leds[led_num] == 1):
                for t in range(num_tri):
                    lam_scores[t] += multi_surfaces[led_num,t]

        stddev = np.std(lam_scores)
        if(stddev < best_stddev):
            best_stddev = stddev	   
            active_leds = []
            for led_num in range (len(selected_leds)):
                if(selected_leds[led_num] == 1):
		    active_leds.append(led_num)
	
            print str(stddev) + "for led set:"+str(active_leds) + '  (leds: ' + str(np.sum(selected_leds)) + ')'
        else:
            #print str(stddev) + "for led set:"+str(active_leds) + '  (leds: ' + str(np.sum(selected_leds)) + ')'
            if(i%100 == 0): print '(' + str(i) + ')' + str(stddev)

	#modify the led pattern
	#get random positions of active and inactive less, and toggle them (preserving total active count)
        #mirror the top and bottom halves to preserve symmetry
	
	active = rnd.randint(0,21)
	inactive = rnd.randint(1,22)

	jump_count = 0
	inact_index =0
	while (jump_count < inactive):
	    inact_index += 1
	    jump_count += 1 - selected_leds[inact_index]

	#print 'inact ' + str(inact_index) + ' (' + str(inactive) + ')'
 
 	jump_count = -1
	act_index =0
	while (jump_count < active):
	    act_index += 1
	    jump_count += selected_leds[act_index]

	#print 'act ' + str(act_index)
 
 	selected_leds[inact_index] = 1
 	selected_leds[91 - inact_index] = 1
 	selected_leds[act_index] = 0
 	selected_leds[91 - act_index] = 0

	#print sum(selected_leds)

    sys.exit()


'''
# -----------------------------------------------------------
def evaluate_illuminance_score( updateable_line, camerasVertices, triangles, shape_name ):
    """
    Measure illuminance of surfaces.
    Create a set of randomly selected LED sets.
    Ignore LED sets that do not illiminate all sufaces of the spherical model.
    Report the total lambertian score, measured per LED per hit surface. 
    Report the standard deviation of lambertian scores over the set of spherical model surfaces.
    """
    global cameraPos, scale, logged_score_to_file, loggable    

    # BEST_LED_DATAq        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
    # #best_LEDs   = get_best_leds_from_file()
    # print(BEST_LED_DATAq)
    # print(len(BEST_LED_DATAq))
    # best_LEDsq   = [x[0] for x in BEST_LED_DATAq if x[3] == '1']
    # print(best_LEDsq)
    # print(len(best_LEDsq))
    # sys.exit()

    string = []        
    drawTextString = []
    l,r,d = 0,0,0
    all_leds        = draw_dome( scale , False )
    print
    sequence_size   = 44
    max_depth       = 1
    led_sequence    = all_leds[:91] #[4,7,10,11,12,69,72,81,86,87,14,15,16,17,19,21,22,23,30,33,54,56,57,59,62,65,66,68,75,78,26,29,32,35,38,39,40,42,43,46,49,51,52,55,58,60,61,63,64,67,24,25,27,28,31,34,36,37,41,44,45,47,48,50,53,70,73,76,79,82,8,9,13,18,20,71,74,77,80,83,1,2,3,5,6,84,85,88,90,91,0,89];
    index_stop_search   =  1
    
    led_sets        = monte_carlo_sequences.get_led_sets_selected(all_leds, led_sequence, sequence_size, max_depth, index_stop_search)
    
    candidate_led_sets = []         
    led_sets_compute = 0
    progress = 0

    led_set = [] 
    for index in led_sequence[:44]:
        led_set.append(all_leds[index])         
    print(stdev_selected_set(triangles, led_set))
    sys.exit()
    startTime = currentMillis()
    if not DO_EVALUATIONS:
        leds                = [updateable_line.get_point()] # Use reflections from single light selected by arrow-keys.
        triangles           = TARGET_TRIANGLES[:10]
        shape_name          = "Test Tri"
        led_sets            = led_sets[0]
    else:
        file_io.write_to_csv(["led_set", "total_set_lambertian_score", "standard deviation"], "../", "lambertian_led_sets_search.csv")
    # Note: One led hits 50% of surfaces.
        
    for leds in led_sets:                   # For all sets of LED positions with set magnitude 42.
        surfaces    =  get_surface_evaluations(triangles, leds)
        

        #print the progression of the total computes
        led_sets_compute+=1
        percent = int(led_sets_compute *100 / len(led_sets))
        if( percent > progress):
            progress = percent
            print 'Progress : {} %'.format(progress)

        if are_all_surfaces_hit(surfaces) == False:
            break
        else:
            #if yes we can have the total lambertian score and standard deviation for this set and write it in the csv file
            row = write_led_set_lambertian_scores_appended_result_file(all_leds, surfaces, leds)
            candidate_led_sets.append(row)


    print(str(len(candidate_led_sets)) + " sequences computes")
    candidate_led_sets = sorted(candidate_led_sets, key=lambda candidate_led_sets:candidate_led_sets[2])
    best_candidate_leds_index_set = candidate_led_sets[0][0]

    write_led_result_file(all_leds, best_candidate_leds_index_set)

    sys.exit()
    

def are_all_surfaces_hit(surfaces):
        #let us know if all the surfaces are hit
        all_surfaces_hit = True
        for score in surfaces:
            if (score == 0):
                all_surfaces_hit = False
                break
        return all_surfaces_hit


def write_led_set_lambertian_scores_appended_result_file(all_leds, surfaces, leds_vertex_set, filename_suffix="", path_prefix="", extra_row_data=[]):
        """
        path_prefix: should end in "/". It will be used to make a new directory, if the directory, to which the path_prefix points, does not exist.
        extra_row_data: a list-like object. Appended to the CSV row written to file.
        """
        total_set_lambertian_score = np.sum(surfaces)
        stdev_set = np.std(surfaces)
        mean = np.mean(surfaces)
        median = np.median(surfaces)
        min_ =  min(surfaces)
        max_ = max(surfaces)
        iqrange = iqr(surfaces)
        
        led_index = []
        for index in range(len(all_leds)):
             if all_leds[index] in leds_vertex_set:
                 led_index.append(index)
        row = [len(leds_vertex_set), len(all_leds)] + [total_set_lambertian_score, mean, stdev_set, median, iqrange, min_, max_] + extra_row_data + [surfaces] + [time.strftime("%Y-%m-%d-%H-%M-%S")] + led_index
        file_io.write_to_csv(row, "../"+str(path_prefix), "lambertian_led_sets"+str(filename_suffix)+".csv")
        return row


def write_led_result_file(all_leds, candidate_leds_index_set):
    for led_index in range(len(all_leds)):
        row = [led_index, 0, 0, 0]
        if led_index in candidate_leds_index_set:
            row[3] = 1
        file_io.write_to_csv(row, "../", "best_stdev_led_set"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv")
        #"led_scores_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv"


def get_surface_evaluations(triangles, leds):
    surfaces    = [0] * len(triangles)
    
    for led in leds:                    # For all 42 leds:
        for tri_num in range(len(triangles)):
            tri = triangles[tri_num]
            make_triangle_face( tri )
            c  = find_center_of_triangle( tri )
            n1 = find_perpendicular_of_triangle( tri )              # Get normal of current tri plane.
            l, r    = reflect_no_rotate( c, led, n1 )
            """ usage of l and r require a prior-translate to c.
            """
            if is_front_facing_reflection(tri, l, r):       #Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )
            
                draw_incident_ray(c, l)
                draw_reflection_ray(c, r)
                #view = np.subtract(cameraPos, c)    #reposition relative to center of incident surface.
                lamb_diffuse        = reflect_models.Lambert_diffuse( incident_vector=l, surface_norm=n1 )

                score               = lamb_diffuse  # Get Lambertian intensity value (x1) per surface per led. --> [surface] = accumulated score.
                surfaces[tri_num]   += score
    return surfaces
'''

# calculate the target surface illumination for all led for all faces 
def get_full_set_surface_evaluations(triangles, leds):
    surfaces = np.zeros((len(leds),len(triangles)))
    for led_num in range(0, len(leds)) :                    # For all of the leds:
        for tri_num in range(0,len(triangles)):
            tri = triangles[tri_num]
            make_triangle_face( tri )
            c  = find_center_of_triangle( tri )
            n1 = find_perpendicular_of_triangle( tri )              # Get normal of current tri plane.
            l, r    = reflect_no_rotate( c, leds[led_num], n1 )
            """ usage of l and r require a prior-translate to c.
            """
            if is_front_facing_reflection(tri, l, r):       #Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )
                draw_incident_ray(c, l)
                lamb_diffuse        = reflect_models.Lambert_diffuse( incident_vector=l, surface_norm=n1 )

                score               = lamb_diffuse  # Get Lambertian intensity value (x1) per surface per led. --> [surface] = accumulated score.
                surfaces[led_num][tri_num]   += score
    return surfaces



def stdev_selected_set(triangles, leds):
    
    surfaces    = get_surface_evaluations(triangles, leds)
    
    stdev_set = 0
    all_surfaces_hit = 1
    for score in surfaces:
        if (score == 0):
            all_surfaces_hit = 0
            break

    #if yes we can have the total lambertian score and standard deviation for this set and write it in the csv file
    if(all_surfaces_hit == 1):
        total_set_lambertian_score = np.sum(surfaces)
        stdev_set = np.std(surfaces)
    return stdev_set


'''

