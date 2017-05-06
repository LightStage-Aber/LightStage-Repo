from __future__ import print_function
from __future__ import division
from abc import ABCMeta

import time;     currentMillis = lambda: int(round(time.time() * 1000))
from evaluation_methods.helper_illuminance import   get_surface_evaluations, are_all_surfaces_hit, \
                                                    write_led_set_lambertian_scores_appended_result_file
from visualisations import draw_point, draw_wire_sphere, make_triangle_face


class EvaluatorGeneric(object):
    """
    Abstract Base Class (ABC) for LED position optimsation evaluators.
    """
    __metaclass__ = ABCMeta

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
        assert are_all_surfaces_hit(surfaces) , "FAILED: Some surfaces were not hit by these LED Light Vertex positions. Result not written to file. Aborting"

        extra_row_data = [self.shortname , self._source_filename, type(self).__name__]
        row = write_led_set_lambertian_scores_appended_result_file(leds_vertices, surfaces, leds_vertices, filename_suffix="_"+type(self).__name__, path_prefix=self._path_prefix, extra_row_data=extra_row_data)

        print("Evaluator type: " + str(type(self).__name__))
        print("Source Filename: " + str(self._source_filename))
        print("Finished with standard deviation:" + str(row[4]))
        print("Finished with normalised standard deviation:" + str(float(row[4]) / len(leds_vertices)))
        print("Finished with Num of LEDS: " + str(len(leds_vertices)))

    def tune(self, triangles, leds_vertices ):
        """
        Tune the intensities of the mapped leds vertex positions to balance the standard deviation. (Do after evaluating the standard deviation of lambertian illuminance of the terget shape).
        """
        #Todo: Test and refactor for generic tuning:
        assert False, "Requires refactoring and re-testing."
        surfaces = get_surface_evaluations(triangles, leds_vertices)
        if not are_all_surfaces_hit(surfaces):
            print("---FAILED--- to hit all surfaces. Result not written to file.")
        else:
            intensities = [1.0]*len( leds_vertices )
            tri_centers = obj_model_reader.get_triangle_centers(triangles)
            assert len(tri_centers) > 1, "Unwrapping of obj model triangles leads to " + str(len(tri_centers)) \
                                         + " triangles. In:\n" + str(tri_centers)

            # Todo: Pass in tuner object at __init__, then call tuner.tune(xyz). Do this instead of static call.
            res = Tuning.selector(led_vertices = leds_vertices,
                                    led_intensities = intensities,
                                    surface_tris = triangles,
                                    surface_center_vertices = tri_centers,
                                    surface_values = surfaces)

            #Todo: Test written tuning results are accurate. - Check output surface_values etc.
            assert False, "Test written tuning results are accurate. - Check output surface_values etc."
            intensities = res.x
            surfaces = []
            extra_row_data = [self.shortname , self.objfilename, type(self).__name__, intensities]
            row = write_led_set_lambertian_scores_appended_result_file(leds_vertices, surfaces, leds_vertices, filename_suffix="_tuning", path_prefix=self.path_prefix, extra_row_data=extra_row_data)
            print("Mapped Vertex Positions:\n"+str(leds_vertices) if len(leds_vertices) < 10 else "")
            print("Finished with standard deviation:" + str(row[2]))
            print("Finished with normalised standard deviation:" + str( float( row[2] / len(leds_vertices) )))
            print("Finished with Num of LEDS: "+str(len(leds_vertices)))
