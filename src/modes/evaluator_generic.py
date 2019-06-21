from __future__ import print_function
from __future__ import division

from OpenGL.GL import GL_FRONT, GL_AMBIENT_AND_DIFFUSE, GL_SPECULAR, GL_SHININESS, glMaterialfv, glMaterialf

import numpy as np
import time;     currentMillis = lambda: int(round(time.time() * 1000))
from illuminance.helper_illuminance import   get_surface_evaluations, are_all_surfaces_hit, get_statistics_on_data, write_illumination_result_data_to_file, write_led_set_lambertian_scores_appended_result_file
from visualisations import draw_point, draw_wire_sphere, make_triangle_face, draw_wire_frame_of_obj_from_filename, draw_text
from brightness_control_tuning.tuning_selector import BrightnessControlStrategy, TuningInputDataContainer, TuningOutputDataContainer

from options import *

class EvaluatorGeneric(object):
    """
    Abstract Base Class (ABC) for LED position optimsation evaluators.
    """
    # warned=False
    def display(self, triangles, frame, leds_vertices):
        """
        Draw the target shape and light vertex positions.
        """
        dict_properties = getPropertiesFile("../properties/default.properties")
        _frame_objfilename = dict_properties['FrameModel']['frame.objfilename']
        _frame_scale = float(dict_properties['FrameModel']['frame.scale'])


        # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.0, 0.0, 0.0, 1))
        # glMaterialfv(GL_FRONT, GL_SPECULAR, (0, 0, 0, .2))
        # glMaterialf(GL_FRONT, GL_SHININESS, 20)
        draw_wire_frame_of_obj_from_filename(_frame_objfilename, scale=float(_frame_scale)*1.04)
        # if not EvaluatorGeneric.warned:
        #     print("Frame has n mounting points available:"+str(len(frame)))
        #     EvaluatorGeneric.warned=True

        # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.0, 0.0, 1))
        # glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 0, 0, .2))
        # glMaterialf(GL_FRONT, GL_SHININESS, 20)
        for j in range(len(frame)):
            draw_point( frame[j], size=8 ) if frame[j] is not None else None
        

        # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.0, 0.0, 1))
        # glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 0, 0, .2))
        # glMaterialf(GL_FRONT, GL_SHININESS, 20)
        for i in range(len(leds_vertices)):
            led = leds_vertices[i]
            draw_wire_sphere( vertex=led, size=0.35, scale=1 ) if led is not None else None
        

        # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.0, 1.0, 0.0, 1))
        # glMaterialfv(GL_FRONT, GL_SPECULAR, (1, 1, 1, .2))
        # glMaterialf(GL_FRONT, GL_SHININESS, 99)
        for tri in triangles:
            make_triangle_face( tri )
        #draw_text("", 10, 10, DISABLE_LIGHTING=False, translate_point=leds_vertices[0])
        

    def evaluate(self, triangles, leds_vertices, intensities):
        """
        Evaluate the standard deviation of lambertian illuminance of the terget shape, from the loaded leds vertex positions.
        """
        surfaces = get_surface_evaluations(triangles, leds_vertices, intensities)
        if not are_all_surfaces_hit(surfaces):
            print("---FAILED--- to hit all surfaces. Result not written to file.")
            # assert are_all_surfaces_hit(surfaces) , "FAILED: Some surfaces were not hit by these LED Light Vertex positions. Result not written to file. Aborting"
        else:
            header_data, row_data = get_statistics_on_data( surfaces=surfaces, all_leds=leds_vertices, leds_vertex_set=leds_vertices, intensities=intensities, 
                                                            evaluator_shortname=self.shortname , source_filename=self._source_filename, evaluator_class=type(self).__name__ )
            write_illumination_result_data_to_file(header_data, row_data, filename_suffix="_"+type(self).__name__, path_prefix=self._path_prefix)
            result_dict_data = dict(zip(header_data, row_data))
                        
            self.__print_evaluation_results( result_dict_data )


    def tune(self, triangles, leds_vertices, intensities ):
        """
        Tune the intensities of the mapped leds vertex positions to balance the standard deviation.
        """
        _start_intensities = intensities[:]
        surfaces = get_surface_evaluations(triangles, leds_vertices, intensities)
        if not are_all_surfaces_hit(surfaces):
            print("---FAILED--- to hit all surfaces. Result not written to file.")
        else:
            input_data = TuningInputDataContainer(surface_tris=triangles , led_vertices=leds_vertices, intensities=intensities)
            output_data = BrightnessControlStrategy().selector(input_data)

            intensities = output_data.intensities
            surfaces = output_data.surface_scores

            # Result data:
            header_data, row_data = get_statistics_on_data( surfaces=surfaces, all_leds=leds_vertices, leds_vertex_set=leds_vertices, intensities=intensities, 
                                                            evaluator_shortname=self.shortname , source_filename=self._source_filename, evaluator_class=type(self).__name__ )
            write_illumination_result_data_to_file(header_data, row_data, filename_suffix="_"+type(self).__name__, path_prefix=self._path_prefix)
            result_dict_data = dict(zip(header_data, row_data))

            self.__print_evaluation_results( result_dict_data )
            self.__print_tuning_results(intensities, _start_intensities)
    

    
    """
        ------- Private functions follow --------
    """

    def __print_evaluation_results(self, result_dict_data):
        """
            Private function to output result data to STDOUT after evaluation and tuning operations completes.
        """
        print("Evaluator type: " + str(type(self).__name__))
        print("Source Filename: " + str(self._source_filename))
        print("Finished with standard deviation:" + str( result_dict_data["surface_stdev"] ))
        if not result_dict_data["UNIFORM_LED_INTENSITIES"]:
            print("Warning: Be aware that the normalised standard deviation (Std/Qty) metric is *unreliable* when adjusting Qty and using non-uniform light intensities (a second dependent variable).")
        # -------------------------------------------------------------------------------------------------------------
        # Do not change the format of this STDOUT line, tests will fail.
        # The test harness depends on this output string's exact content:
        # @todo: make this not a hack: Introduce a results object, accessible from test harness.
        print("Finished with normalised standard deviation:" + str(result_dict_data["normalised_stdev_n"]))
        # -------------------------------------------------------------------------------------------------------------
        print("Normalised standard deviation is std(surface lumens)/num_leds")
        print("Finished with Evenness (/n):" + str(result_dict_data["normalised_stdev_n"]))
        print("Finished with Evenness (/n/mean_intensity):" + str(result_dict_data["normalised_stdev_n_intensity"]))
        print("Finished with Relative Standard Deviation/ Coefficient Variation (std/mean):" + str(result_dict_data["coefficient_of_stdev"]))
        print("Finished with Median:" + str(result_dict_data["surface_median"]))
        print("Finished with IQR:" + str(result_dict_data["surface_iqrange"]))
        print("Finished with Relative IQR (IQR/Median):" + str(result_dict_data["coefficient_of_iqr_median"]))
        print("Finished with Num of LEDS: " + str( result_dict_data["Qty_Available_LED_Indexes"] ))


    def __print_tuning_results(self, intensities, _start_intensities):
        """
            Private function to output result data to STDOUT after evaluation and tuning operations completes.
        """
        print("Count of LEDs with changed output intensities: " + str(  [x != y for x,y in zip(intensities, _start_intensities)].count(True)  )+" of "+str(len(intensities)))
        print("Mean Difference of changed output intensities: " + str(  (np.mean(intensities) - np.mean(_start_intensities)) ) + " Prior:" + str(np.mean(_start_intensities))+ " Post:" + str(np.mean(intensities)) )
        print("-----------------------------------------------------")
        print("(See Output Results File for Tuned Intensity Values)")
        print("-----------------------------------------------------")