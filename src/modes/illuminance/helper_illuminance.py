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
    
    def __precondition(intensities):

        has_intensities_data = intensities is not None        
        if not has_intensities_data:
            default_intensity_allowed = property_to_boolean(section="LightOutput", key="light.output_intensity_from_index.allow_default")
            if default_intensity_allowed:
                _default_value = property_to_number(section="LightOutput", key="light.output_intensity_from_index.default_value", vmin=0.0, vmax=10.0, vtype=float)
                intensities = [_default_value]*len(leds)
                print("Warning: Replaced light intensities data with "+str(intensities))
            else:
                assert default_intensity_allowed, ("Replacement of intensity values is disallowed (in the event of invalid intensity data).\n" + 
                    "Set config to light.output_intensity_from_index.allow_default=True. Exiting.\n" + 
                    "Received intensity data: "+str(intensities))
                import sys; sys.exit()
        else:
            # all is good
            pass
        return intensities

    intensities = __precondition(intensities)
    print("Attempt Evaluation with LED Intensities (truncated to indexes [0-4]): "+str(intensities[:5])+" Mean: "+str(np.mean(intensities)))

    for led_num in range(len(leds)):  # For all n leds:
        led = leds[led_num]
        intensity = intensities[led_num]
        for tri_num in range(len(triangles)):
            tri = triangles[tri_num]
            # make_triangle_face( tri )
            score = do_surface_evaluation_single_LED(tri, led, intensity)
            surfaces[tri_num] += score

    return surfaces


def do_surface_evaluation_single_LED(tri, led, intensity):
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


def get_statistics_on_data(surfaces, all_leds, leds_vertex_set, intensities, evaluator_shortname , source_filename, evaluator_class ):
    
    # Standard Stats Data
    total_set_lambertian_score = np.sum(surfaces)
    unnormalised_stdev_set = np.std(surfaces)
    mean = np.mean(surfaces)
    median = np.median(surfaces)
    min_ = min(surfaces)
    max_ = max(surfaces)
    iqrange = iqr(surfaces)

    # Metric & More Complex Stats Data 
    MEAN_INTENSITY = np.mean(intensities) #property_to_number(section="MEAN_INTENSITY", key="MEAN_INTENSITY", vmin=None, vmax=None, vtype=float)
    UNIFORM_LED_INTENSITIES = all([v == MEAN_INTENSITY for v in intensities])
    normalised_stdev_n = float(unnormalised_stdev_set) / len(leds_vertex_set)
    normalised_stdev_n_intensity = float(unnormalised_stdev_set) / len(leds_vertex_set) / MEAN_INTENSITY
    relative_stdev = float(unnormalised_stdev_set) / float(mean)
    relative_iqr_median = iqrange/median

    # Target Object Data
    obj, arg = get_parsed_commandline_options()
    obj.TARGET_SHAPE
    obj.TARGET_SCALE
    obj.TARGET_TRANSLATION

    # Frame Data
    dict_properties = getPropertiesFile("../properties/default.properties")
    frame_objfilename = dict_properties['FrameModel']['frame.objfilename']
    frame_scale = float(dict_properties['FrameModel']['frame.scale'])

    # LED Index Data
    led_index = []
    for index in range(len(all_leds)):
        if all_leds[index] in leds_vertex_set:
            led_index.append(index)
    
    header_row = ["Qty_Selected_LED_Indexes", "Qty_Available_LED_Indexes", 
                    "total_surface_lambertian_score", "normalised_stdev_n", "normalised_stdev_n_intensity", "MEAN_INTENSITY", "UNIFORM_LED_INTENSITIES", "coefficient_of_stdev", "coefficient_of_iqr_median",
                    "surface_mean_score", "surface_stdev", "surface_median", "surface_iqrange", "surface_min","surface_max",
                    "Evaluator_Shortname" , "source_filename", "Evaluator_ClassName",
                    "frame_objfilename", "frame_scale",
                    "obj.TARGET_SHAPE", "obj.TARGET_SCALE", "obj.TARGET_TRANSLATION", 
                    "surfaces_raw_data",
                    "timestamp",
                    "light_indexes",
                    "light_vertices",
                    "light_intensities"
                    ]                
    row = [len(leds_vertex_set), len(all_leds)] + [
                    total_set_lambertian_score, normalised_stdev_n, normalised_stdev_n_intensity, MEAN_INTENSITY, UNIFORM_LED_INTENSITIES, relative_stdev, relative_iqr_median] + [
                    mean, unnormalised_stdev_set, median, iqrange, min_, max_] + [
                    evaluator_shortname , source_filename, evaluator_class] + [
                    frame_objfilename, frame_scale] + [
                    obj.TARGET_SHAPE, obj.TARGET_SCALE, obj.TARGET_TRANSLATION] + [
                    surfaces] + [
                    time.strftime("%Y-%m-%d-%H-%M-%S")] + [
                    led_index] + [
                    all_leds] + [
                    intensities ]
    return header_row, row


def write_illumination_result_data_to_file(header_data, row_data, filename_suffix, path_prefix):
    """
    path_prefix: should end in "/". It will be used to make a new directory, if the directory, to which the path_prefix points, does not exist.
    extra_row_data: a list-like object. Appended to the CSV row written to file.
    """    
    csv_path = "../" + str(path_prefix)
    csv_filename = "Results_Illuminance_" + str(filename_suffix) + ".csv"
    
    # Write header, if file not exist:
    if not os.path.exists(csv_path + csv_filename):
        file_io.write_to_csv(header_data, csv_path, csv_filename)
        print("Header written to: "+str(csv_path)+str(csv_filename))
    
    # Write row data:
    file_io.write_to_csv(row_data, csv_path, csv_filename)
    print("Data written to: "+str(csv_path)+str(csv_filename))













# ---------------------------------------------------------------------------------------
#                   Deprecated / PendingDeprecation functions follow:
# ---------------------------------------------------------------------------------------# ---------------------------------------------------------------------------------------


def write_led_set_lambertian_scores_appended_result_file(all_leds, surfaces, leds_vertex_set, filename_suffix="",
                                                         path_prefix="", extra_row_data=[]):
    """
    path_prefix: should end in "/". It will be used to make a new directory, if the directory, to which the path_prefix points, does not exist.
    extra_row_data: a list-like object. Appended to the CSV row written to file.
    
    @deprecated - Note, this function is deprecated and may be removed in future.
    Superseded by get_statistics_on_data() and write_illumination_result_data_to_file() functions.
    """
    import warnings
    warnings.warn("@DeprecationWarning", DeprecationWarning)

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
    header_row = ["Qty_Selected_LED_Indexes", "Qty_Available_LED_Indexes", 
                    "total_surface_lambertian_score", 
                    "normalised_stdev_n", "normalised_stdev_n_intensity", "MEAN_INTENSITY", "UNIFORM_LED_INTENSITIES", "relative_stdev", "relative_iqr_median",
                    "surface_mean_score", "surface_stdev", "surface_median", "surface_iqrange", "surface_min","surface_max",
                    "Evaluator_Shortname" , "source_filename", "Evaluator_ClassName",
                    "surfaces_raw_data",
                    "timestamp",
                    "light_indexes",
                    "light_intensities"
                    ]
    row = [len(leds_vertex_set), len(all_leds)] + [total_set_lambertian_score] + extra_row_data[0] + [mean, unnormalised_stdev_set, median, iqrange, min_,
                                                   max_] + extra_row_data[1] + [surfaces] + [
              time.strftime("%Y-%m-%d-%H-%M-%S")] + [led_index]

              
    csv_path = "../" + str(path_prefix)
    csv_filename = "lambertian_led_sets" + str(filename_suffix) + ".csv"
    
    # Write header, if file not exist:
    if not os.path.exists(csv_path + csv_filename):
        file_io.write_to_csv(header_row, csv_path, csv_filename)
        print("Header written to: "+str(csv_path)+str(csv_filename))
    # Write row data:
    file_io.write_to_csv(row, csv_path, csv_filename)
    print("Data written to: "+str(csv_path)+str(csv_filename))
    return row


def write_led_result_file(all_leds, candidate_leds_index_set):

    """
    @deprecated - Note, this function is pending deprecation decision and may be removed in future.
    Superseded by get_statistics_on_data() and write_illumination_result_data_to_file() functions.
    """
    import warnings
    warnings.warn("@PendingDeprecationWarning", PendingDeprecationWarning)

    for led_index in range(len(all_leds)):
        row = [led_index, 0, 0, 0]
        if led_index in candidate_leds_index_set:
            row[3] = 1
        file_io.write_to_csv(row, "../", "best_stdev_led_set" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv")
        # "led_scores_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv"

