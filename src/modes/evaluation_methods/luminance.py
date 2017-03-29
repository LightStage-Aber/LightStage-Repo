"""
    Luminance Module: 
     - Module containing algorithmic approaches that quantify based on amount of "light reflected from the surface of a target object into the camera(s)".
"""
from __future__ import division
#from abc import ABCMeta
import random as rnd
import time;     currentMillis = lambda: int(round(time.time() * 1000))

from options import *
from file_utils import *
from ..manipulate_results_data import *
from ..visualisations import *
from model_helpers.vector_maths import rotate_triangles
import surface_coverage_metric
from coverage_datastructure import accumulated_coverage_datastructure

from ..evaluations import Evaluator






class MeasureReflectanceIntoCameras( Evaluator ):
    """
    Class to evaluate the reflectance of light into cameras, bounced from an object.
    
    This uses rotations of the object.
    This uses cameras, into which light reflects.
    The light positions are fixed at the vertices of the dome.
    This method uses two metrics:
        - surface coverage, are all surfaces of the object hit. 
            - Selecting LEDS from the essential LEDS (collectively hits all surfaces) and then most desirable LEDS (hits most number of surfaces).
            - Search through the most desirable LEDS for highest quantity of surface hits, using a depth search solution.
        - luminance score, accumulate the amount of diffuse/specular light reflected into the cameras.
    
    """
    def __init__(self):
        self.lumination_coverage_datastructure = accumulated_coverage_datastructure()

    def display(self, triangles, shape_name, kwords={}):
        pass

    def evaluate( self, updateable_line, camerasVertices, triangles, shape_name, camera_layout, kwords ):
            """
            Metric A: Measure reflection luminance at camera positions; using lambertian and optionally specular reflectance.
            Metric B: Measure quantity of tri surfaces hit by LED incidence ray.
            Use case C: show demo of only 10 tris, showing [LED incidence ray into tris and reflectance into cameras] and [Metric A score] and [Metric B score].
            """
            loggable = []
            string = []        
            drawTextString = []
            l,r,d = 0,0,0
            leds = kwords['all_leds']
            
            
            # Material Configuration:
            MAT_SHININESS = 1
            DIFFUSE_SHADING_DESCRIPTION  = "Shading Diffuse: Lambertian cosine"
            SPECULAR_SHADING_DESCRIPTION = "Shading Specular: Blinn-Phong with material shininess exponent: "+str(MAT_SHININESS)
            SHADING_LIGHT_DESCRIPTION    = "Light RGBA Channel(s): A single channel without multiplier is used, equivalent to RGBA(1,0,0,1)"
            SHADING_MATERIAL_DESCRIPTION = "Material RGBA Channel(s): A single channel without multiplier is used, equivalent to RGBA(1,0,0,1)"
            
            
            startTime = currentMillis()
            """
            In test mode, present only 10 triangles to visualise reflections, etc at a small scale.
            """
            if not kwords['DO_EVALUATIONS']:
                leds                = [updateable_line.get_point()] # Use reflections from single light selected by arrow-keys.
                kwords['TARGET_ROTATIONS']    = 1                             # Remove rotations.
                triangles           = triangles[:10]
                shape_name          = "Test Tri"
            
            reflection_score = 0
            triangleHit_score = 0
            for led_num in range(len(leds)):
                led_score = 0                               # The accumulated scaled reflection-angle-to-each-camera-from-specular-angle score.
                led_tri_hit_score = 0                       # The number of tris the led has hit.
                led = leds[led_num]
                
                
                if kwords['DO_EVALUATIONS']:
                    progress_complete   = round((led_num+1)*(100.0/len(leds)),0)
                    progress_time       = round(((currentMillis()-startTime)/1000.0)/60,2)
                    est_time_left       = round((100-progress_complete)*(progress_time/progress_complete),2) if progress_complete > 5 else "--"
                    print(str(progress_complete)+"% at "+str(progress_time)+" mins with est. remaining "+str(est_time_left)+" mins.")
                
                for rotation_num in range(kwords['TARGET_ROTATIONS']):  
                    if kwords['DO_EVALUATIONS']:
                        triangles = rotate_triangles(triangles, axis=kwords['TARGET_ROTATION_AXIS'], degrees=kwords['TARGET_ROTATION_DEGREES'])
                    for tri_num in range(len(triangles)):
                        tri = triangles[tri_num]
                        make_triangle_face( tri )
                        c  = find_center_of_triangle( tri )
                        n1 = find_perpendicular_of_triangle( tri )              # Get normal of current tri plane.
                        l, r    = reflect_no_rotate( c, led, n1 )
                        """ usage of l and r require a prior-translate to c.
                        """
                        if is_front_facing_reflection(tri, l, r):       #Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )
                            for cam_num in range(len(camerasVertices)):
                                cam = camerasVertices[cam_num]
                                if is_front_facing_reflection_to_camera(tri, cam):
                                    
                                    draw_reflection_to_camera( [cam], tri )
                                    draw_incident_ray(c, l)
                                    draw_reflection_ray(c, r)
                                    view = np.subtract(cam, c)    #reposition relative to center of incident surface.
                                    rad,d = get_angle_from_reflection_to_camera(c, r, view)
                                    
                                    blinn_spec           = reflect_models.BlinnPhong_specular(incident_vector=l, view_vector=view, surface_norm=n1, shininess_exponent=MAT_SHININESS)
                                    lamb_diffuse         = reflect_models.Lambert_diffuse( incident_vector=l, surface_norm=n1 )

                                    this_led_score       = self.get_reflectance_score( lamb_diffuse , blinn_spec )
                                    led_score           += this_led_score
                                    
                                    if kwords['DO_EVALUATIONS']:
                                        coverage_score  = this_led_score
                                        self.lumination_coverage_datastructure.add( coverage_score, led_num, tri_num)
                                    else:
                                        drawTextString.append("Camera "+str(cam_num)+": "+str(round(d,2))+"d;    "+str(round(blinn_spec,2))+" + "+str(round(lamb_diffuse,2))+" = "+str(round(this_led_score,2)) )

                            led_tri_hit_score +=1
                
                if kwords['DO_EVALUATIONS']:
                    if not kwords['logged_score_to_file']:
                        loggable.append( [led_num, led_score, led_tri_hit_score] )
                    reflection_score += led_score
                    triangleHit_score += led_tri_hit_score
            
    #        print "Time taken: "+str(round((currentMillis()-startTime)/1000.0,2))+" seconds"
    #        print("Coverage Score",best_score, best_leds)
            if kwords['DO_EVALUATIONS']:
                led_to_tri_reflection_map           = self.lumination_coverage_datastructure.get()
                best_score, best_config, best_leds  = surface_coverage_metric.get_led_configuration_with_best_coverage( 
                                                                                  led_to_tri_reflection_map, 
                                                                                  len(triangles), 
                                                                                  max_quantity_of_leds_required=kwords['QTY_OF_BEST_LEDS_REQUIRED'], 
                                                                                  max_depth=2,
                                                                                  max_steps=10, 
                                                                                  ignore_tri_lighting_error=True, 
                                                                                  ignore_led_lighting_error=True )
                for i in range(len(loggable)):
                    led_n = loggable[i][0]
                    is_selected = 1 if led_n in best_leds else 0
                    loggable[i].append( is_selected )
                
                
                
                log_score            = file_io.file_writer(path="../",filename="led_scores_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv") if not kwords['SELECT_BEST_LEDS'] else None
                log_meta_data        = file_io.file_writer(path="../",filename="led_meta_data_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".txt") if not kwords['SELECT_BEST_LEDS'] else None
                data_header          = ["led_num","reflection_score","tri_hit_score"]
                data_header.append( "coverage_error="+str(best_score))
                
                endTime = currentMillis()
                if not kwords['logged_score_to_file']:
                    loggable = [data_header]+loggable
                
                    string.append("Logged led scores to file: "+str(log_score.get_filepath()))
                    string.append("Logged meta data to file: "+str(log_meta_data.get_filepath()))
                    string.append("Target Model: "+str(shape_name))
                    string.append("Target Scaling Factor: "+str(kwords['TARGET_SCALE']))
                    string.append("Target Translation: "+str(kwords['TARGET_TRANSLATION']))
                    string.append("Reflection Score: "+str(reflection_score))
                    string.append("Triangle Hit Qty Score: "+str(triangleHit_score))
                    string.append("Triangle Coverage Error Score: "+str(best_score))
                    string.append("Quantity of LEDs for Coverage Error: "+str(kwords['QTY_OF_BEST_LEDS_REQUIRED']))
                    string.append("Time taken: "+str(round((endTime-startTime)/1000.0,2))+" seconds")
                    string.append("Quantity of LEDs: "+str(len(leds)))
                    string.append("Quantity of Tris: "+str(len(triangles)))
                    string.append("Quantity of Cameras: "+str(len(camerasVertices)))
                    string.append("Camera position description: "+camera_layout.getDescription())
                    string.append("Camera positions: "+str(camerasVertices))
                    string.append("Quantity of Target Rotations: "+str(kwords['TARGET_ROTATIONS']))
                    string.append("Target Axis Rotation: "+str(kwords['TARGET_ROTATION_AXIS'])+", "+str(kwords['TARGET_ROTATION_DEGREES'])+" degrees")
                    string.append( DIFFUSE_SHADING_DESCRIPTION  )
                    string.append( SPECULAR_SHADING_DESCRIPTION )
                    string.append( SHADING_LIGHT_DESCRIPTION   )
                    string.append( SHADING_MATERIAL_DESCRIPTION )
                    
                    PARSE_OPTIONS,PARSE_ARGS = get_parsed_commandline_options()
                    string.append( "Command line arguments: "+str(PARSE_ARGS) )
                    string.append( "Command line options parsed: "+str(PARSE_OPTIONS) )
                    
                    log_score.write_to_csv_rows( loggable )
                    log_meta_data.write_to_file_list(string, append_newline=True)
                    #logged_score_to_file = True
                    print "-------------------"
                    for s in string:
                        print s
                    print "-------------------"
                    sys.exit()
            else:
                led_display_header = "LED "+str(updateable_line.get_index())+" Degrees ReflectRay-to-Cam; Specular Intensity + Diffuse Intensity = Total Intensity"
                drawTextString.append("-"*len(led_display_header))
                drawTextString.append(led_display_header)
                drawTextString.reverse()
                for i in range(len(drawTextString)):
                    draw_text(drawTextString[i],20,20+(i*15))
            

    def get_reflectance_score( self, lamb_diffuse , blinn_spec ):
        PARSE_OPTIONS,PARSE_ARGS = get_parsed_commandline_options()
        
        return lamb_diffuse if PARSE_OPTIONS.DIFFUSE_REFLECTANCE_ONLY == 1 else lamb_diffuse + blinn_spec



