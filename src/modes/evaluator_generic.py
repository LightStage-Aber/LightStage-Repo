from __future__ import print_function
from __future__ import division

from OpenGL.GL import GL_FRONT, GL_AMBIENT_AND_DIFFUSE, GL_SPECULAR, GL_SHININESS, glMaterialfv, glMaterialf

import time;     currentMillis = lambda: int(round(time.time() * 1000))
from illuminance.helper_illuminance import   get_surface_evaluations, are_all_surfaces_hit, \
                                                    write_led_set_lambertian_scores_appended_result_file
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
        

    def evaluate(self, triangles, leds_vertices):
        """
        Evaluate the standard deviation of lambertian illuminance of the terget shape, from the loaded leds vertex positions.
        """
        surfaces = get_surface_evaluations(triangles, leds_vertices)
        if not are_all_surfaces_hit(surfaces):
            print("---FAILED--- to hit all surfaces. Result not written to file.")
            # assert are_all_surfaces_hit(surfaces) , "FAILED: Some surfaces were not hit by these LED Light Vertex positions. Result not written to file. Aborting"
        else:
            extra_row_data = [self.shortname , self._source_filename, type(self).__name__]
            row = write_led_set_lambertian_scores_appended_result_file(leds_vertices,
                                                                       surfaces,
                                                                       leds_vertices,
                                                                       filename_suffix="_"+type(self).__name__,
                                                                       path_prefix=self._path_prefix,
                                                                       extra_row_data=extra_row_data)
            normalised_stdev = float(row[4]) / len(leds_vertices)
            relative_stdev = float(row[4]) / float(row[3])
            median = float(row[5])
            iqr = float(row[6])

            print("Evaluator type: " + str(type(self).__name__))
            print("Source Filename: " + str(self._source_filename))
            print("Finished with standard deviation:" + str(row[4]))
            print("Finished with normalised standard deviation:" + str(normalised_stdev))
            print("Finished with Relative Standard Deviation/ Coefficient Variation (std/mean):" + str(relative_stdev))
            print("Finished with Median:" + str(median))
            print("Finished with IQR:" + str(iqr))
            print("Finished with Relative IQR (IQR/Median):" + str(iqr/median))
            print("Finished with Num of LEDS: " + str(len(leds_vertices)))

    def tune(self, triangles, led_vertices ):
        """
        Tune the intensities of the mapped leds vertex positions to balance the standard deviation.
        """
        surfaces = get_surface_evaluations(triangles, led_vertices)
        if not are_all_surfaces_hit(surfaces):
            print("---FAILED--- to hit all surfaces. Result not written to file.")
        else:
            input_data = TuningInputDataContainer(surface_tris = triangles , led_vertices = led_vertices)
            output_data = BrightnessControlStrategy().selector(input_data)

            extra_row_data = [self.shortname , type(self).__name__, output_data.intensities]
            row = write_led_set_lambertian_scores_appended_result_file(all_leds=input_data.led_vertices,
                                                                       surfaces=output_data.surface_scores,
                                                                       leds_vertex_set=input_data.led_vertices,
                                                                       filename_suffix="_tuning",
                                                                       path_prefix=self._path_prefix,
                                                                       extra_row_data=extra_row_data)
            print("Evaluator type: " + str(type(self).__name__))
            print("Source Filename: " + str(self._source_filename))
            print("Finished with standard deviation:" + str(row[4]))
            print("Finished with normalised standard deviation:" + str( float( row[4] / len(input_data.led_vertices) )))
            print("Finished with Num of LEDS: "+str(len(input_data.led_vertices)))
            print("Count of LEDs with Changed Brightness: " + str(len([x != 1.0 for x in output_data.intensities])))
            print("Updated Brightness Intensity Values: " + str(output_data.intensities))