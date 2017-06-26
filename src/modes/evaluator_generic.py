from __future__ import print_function
from __future__ import division

import time;     currentMillis = lambda: int(round(time.time() * 1000))
from illuminance.helper_illuminance import   get_surface_evaluations, are_all_surfaces_hit, \
                                                    write_led_set_lambertian_scores_appended_result_file
from visualisations import draw_point, draw_wire_sphere, make_triangle_face
from brightness_control_tuning.tuning_selector import BrightnessControlStrategy, TuningInputDataContainer, TuningOutputDataContainer


class EvaluatorGeneric(object):
    """
    Abstract Base Class (ABC) for LED position optimsation evaluators.
    """

    def display(self, triangles, frame, leds_vertices):
        """
        Draw the target shape and light vertex positions.
        """
        for j in range(len(frame)):
            draw_point( frame[j], size=8 ) if frame[j] is not None else None
        for i in range(len(leds_vertices)):
            led = leds_vertices[i]
            draw_wire_sphere( vertex=led, size=0.1, scale=1 ) if led is not None else None
        for tri in triangles:
            make_triangle_face( tri )

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

            print("Evaluator type: " + str(type(self).__name__))
            print("Source Filename: " + str(self._source_filename))
            print("Finished with standard deviation:" + str(row[4]))
            print("Finished with normalised standard deviation:" + str(normalised_stdev))
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