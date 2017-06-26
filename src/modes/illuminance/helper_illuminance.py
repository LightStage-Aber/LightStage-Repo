from __future__ import division
from numbers import Number
from model_helpers.stats_helper import iqr
from options import *
from file_utils import *
from ..manipulate_results_data import *
from ..visualisations import *
import time;     currentMillis = lambda: int(round(time.time() * 1000))


def are_all_surfaces_hit(surfaces):
    """
    Let us know if all the surfaces are hit. Is each surface value GT 0.0.
    :param surfaces: assert type(surfaces) == list and all([type(x) == float or type(x) == np.float64 for x in surfaces])
    :return: all([x > 0.0 for x in surfaces])
    """
    assert type(surfaces) == list and all( [isinstance(x, Number) for x in surfaces]), \
        "Surfaces should be a list of elements of type float or type np.float64."
    return all([x > 0.0 for x in surfaces])


def get_surface_evaluations(triangles, leds, intensities=None):
    surfaces = [0.0] * len(triangles)
    intensities = intensities if intensities is not None else [1.0] * len(leds)

    for led_num in range(len(leds)):  # For all n leds:
        led = leds[led_num]
        intensity = intensities[led_num]
        for tri_num in range(len(triangles)):
            tri = triangles[tri_num]
            # make_triangle_face( tri )
            score = do_surface_evaluation_single_LED(tri, led, intensity)
            surfaces[tri_num] += score

    return surfaces


def do_surface_evaluation_single_LED(tri=None, led=None, intensity=None):
    score = 0.0
    c = find_center_of_triangle(tri)
    n1 = find_perpendicular_of_triangle(tri)  # Get normal of current tri plane.
    l, r = reflect_no_rotate(c, led, n1)
    """ usage of l and r require a prior-translate to c.
    """
    if is_front_facing_reflection(tri, l, r):  # Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )

        draw_incident_ray(c, l)
        draw_reflection_ray(c, r)
        # view = np.subtract(cameraPos, c)    #reposition relative to center of incident surface.
        lamb_diffuse = reflect_models.Lambert_diffuse(incident_vector=l, surface_norm=n1, intensity=intensity)

        score = lamb_diffuse  # Get Lambertian intensity value (x1) per surface per led. --> [surface] = accumulated score.

    return score


def write_led_set_lambertian_scores_appended_result_file(all_leds, surfaces, leds_vertex_set, filename_suffix="",
                                                         path_prefix="", extra_row_data=[]):
    """
    path_prefix: should end in "/". It will be used to make a new directory, if the directory, to which the path_prefix points, does not exist.
    extra_row_data: a list-like object. Appended to the CSV row written to file.
    """
    total_set_lambertian_score = np.sum(surfaces)
    unnormalised_stdev_set = np.std(surfaces)
    mean = np.mean(surfaces)
    median = np.median(surfaces)
    min_ = min(surfaces)
    max_ = max(surfaces)
    iqrange = iqr(surfaces)

    led_index = []
    for index in range(len(all_leds)):
        if all_leds[index] in leds_vertex_set:
            led_index.append(index)
    row = [len(leds_vertex_set), len(all_leds)] + [total_set_lambertian_score, mean, unnormalised_stdev_set, median, iqrange, min_,
                                                   max_] + extra_row_data + [surfaces] + [
              time.strftime("%Y-%m-%d-%H-%M-%S")] + led_index
    csv_path = "../" + str(path_prefix)
    csv_filename = "lambertian_led_sets" + str(filename_suffix) + ".csv"
    file_io.write_to_csv(row, csv_path, csv_filename)
    print("Data written to: "+str(csv_path)+str(csv_filename))
    return row


def write_led_result_file(all_leds, candidate_leds_index_set):
    for led_index in range(len(all_leds)):
        row = [led_index, 0, 0, 0]
        if led_index in candidate_leds_index_set:
            row[3] = 1
        file_io.write_to_csv(row, "../", "best_stdev_led_set" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv")
        # "led_scores_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv"

