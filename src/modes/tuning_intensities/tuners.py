from __future__ import division
from abc import ABCMeta
from numbers import Number
from collections import namedtuple
import numpy as np

from ..evaluation_methods import helper_illuminance
from ..evaluation_methods.helper_illuminance import get_surface_evaluations
from scipy_optimize_wrapper import SearchEvaluator, SearchScipyOptimize


class Tuner():
    """
    Abstract Base Class (ABC) for search evaluators.
    """
    __metaclass__ = ABCMeta

    def __init__(self, led_vertices=None, led_intensities=None,
                 surface_tris=None, surface_center_vertices=None, surface_values=None):
        self._validate_surface_and_LED_data(led_vertices=led_vertices, led_intensities=led_intensities,
                                            surface_tris=surface_tris, surface_center_vertices=surface_center_vertices,
                                            surface_values=surface_values)

        self.led_vertices = led_vertices
        self.led_intensities = led_intensities
        self.surface_tris = surface_tris
        self.surface_center_vertices = surface_center_vertices
        self.surface_values = surface_values

    def _validate_surface_and_LED_data(self, led_vertices=None, led_intensities=None, surface_tris=None,
                                       surface_center_vertices=None, surface_values=None):
        # TODO: Warning - only partial and naive assertion test coverage provided here.
        assert type(led_vertices) is list and len(led_vertices) > 0 and len(led_vertices[0]) == 3 and type(
            led_vertices[0][0]) == float, \
            "The led vertex positions should be provided in a list of 3 floats. Partial test only."
        assert type(led_intensities) is list and len(led_intensities) > 0 and type(led_intensities[0]) == float, \
            "The led intensity values should be provided as a list of floats. Partial test only."
        assert type(surface_values) is list and len(surface_values) > 0 and type(surface_values[0]) == float, \
            "The triangle surface accumulated intensity values should be provided as a list of floats. Partial test only."
        assert type(surface_tris) is list and len(surface_tris) > 0 and len(surface_tris[0]) == 3 \
               and len(surface_tris[0][0]) == 3 and type(surface_tris[0][0][0]) == float, \
            "The triangle surfaces should be provided as a list of 3 lists of 3 floats."
        assert type(surface_center_vertices) is list and len(surface_center_vertices) > 0 and len(
            surface_center_vertices[0]) == 3 \
               and (type(surface_center_vertices[0][0]) == float or type(surface_center_vertices[0][0]) == np.float64), \
            "The surface triangle center vertex positions should be provided as a list of 3 floats."
        assert len(surface_center_vertices) > 0 and len(surface_center_vertices) == len(surface_values) \
               and len(surface_center_vertices) == len(surface_tris), \
            "All surface data should be of equal quantity."
        assert len(led_vertices) > 0 and len(led_vertices) == len(led_intensities), \
            "All led data should be of equal quantity."
        return True

    def search(self):
        pass


FindMinimum = namedtuple('FindMinimum', 'value data count rounds')
SearchResult = namedtuple('SearchResult', 'std std_norm surface_values intensities rounds')
"""
Immutable Search Result - namedtuple:
@:param std (float) - raw standard deviation of surface value scores.
@:param std_norm (float) - standard deviation of surface value scores, normalised as LED qty agnostic.
@:param surface_values (list[floats]) - evaluated scores
@:param intensities (list[floats]) - intensity values per LED
@:param rounds (int) - number of rounds taken to find result

Usage:
res = SearchResult(std=0.0, std_norm=0.0, surface_values=[], intensities=[], rounds=0)
print(res.std)
"""


class TuneUsingSearch(Tuner):
    def search(self):
        """
        :return: std (float), normalised_std (float), surface_values (list[floats]), updated_intensities (list[floats])
        """
        # the starting point
        x0 = self.led_intensities
        obj = self.EvennessMetricSearch(self)

        minimise = SearchScipyOptimize(obj.evaluate)
        res = minimise.start(x0)
        return res

    class EvennessMetricSearch(SearchEvaluator):
        def __init__(self, tuner):
            assert isinstance(tuner, Tuner), "Should be of type Tuner (the outer class). Construct with access to outer class data."
            self.tuner = tuner

        def evaluate(self, x):
            self.tuner.surface_values = get_surface_evaluations(self.tuner.surface_tris, self.tuner.led_vertices, intensities=x)
            std = np.std(self.tuner.surface_values) / len(self.tuner.led_vertices)
            return std


class TuneUsingIterativeRegressionPDS(Tuner):
    """
    Class to perform tuning using an iterative regression to reduce surface illumination standard deviation.

    The approach iteratively updates LED intensities that affect the surface triangle with the illumination score
    furthest from mean, until the normalised standard deviation error threshold is reached; i.e. the residual error
    falls below the desired threshold.

    This is greedy (best-first) limited local optimsation. It uses the following properties file parameters.

        [Tune]
        tune.mode=1
        tune.regression.threshold=0.005 [Range: >=0]
        tune.regression.max_iterations=100 [Range: >=1]
    """

    def __init__(self, threshold=0.005, max_iterations=100, **kwargs):
        super(TuneUsingIterativeRegressionPDS, self).__init__(**kwargs)  # call super
        self.max_iterations = max_iterations
        self.threshold = threshold
        assert isinstance(self.threshold, Number) and self.threshold >= 0.0, \
            "Residual error threshold should be positive float: " + str(self.threshold) + ". Type: "+str(type(self.threshold))
        assert isinstance(self.max_iterations, Number) and self.max_iterations >= 1, \
            "Max search iterations should be positive int: " + str(self.max_iterations) + ". Type: " + str(type(self.max_iterations))


    def search(self):
        """
        @:return a SearchResult namedtuple containing results from the search - (std=std, std_norm=std_norm, surface_values=surface_values, intensities=intensities, rounds=rounds)
        """
        x = np.std(self.surface_values) / len(self.led_vertices)
        data = self.led_intensities
        find_minimum = self.search(x, data)

        rounds = find_minimum.rounds
        intensities = find_minimum.data['intensities']
        surface_values = find_minimum.data['surfaces']
        std_norm = np.std(surface_values) / len(self.led_vertices)
        std = np.std(surface_values)
        res = SearchResult(std=std, std_norm=std_norm, surface_values=surface_values, intensities=intensities, rounds=rounds)

        return res


    def search(self, x, data):
        default_value = 9999999999999999

        find_minimum = FindMinimum(value=default_value, data=data, count=0, rounds=None)
        rounds = 0
        while x > self.threshold: # Exit when threshold reached
            rounds += 1
            # Do update and evaluation, with corresponding data:
            x, data = self.update(data)
            # Store only best result:
            if x < find_minimum.value:
                find_minimum = FindMinimum(value=x, data=data, count=rounds, rounds=None)
            # Exit when we have been stuck on best value for max_iterations (and only when not default value/first time around loop)
            elif find_minimum.value != default_value \
                    and find_minimum.count + self.max_local_iterations < rounds:
                break
            # print str(round) + ") Normalised standard deviation: " + str(x) + ". Threshold: " + str(self.threshold)

        find_minimum = FindMinimum(value=find_minimum.value, data=find_minimum.data, count=find_minimum.count, rounds=rounds)
        return find_minimum


    def update(self, led_intensities):
        # Si = Find Surface_Value furthest from mean
        s_index = TuneUsingIterativeRegressionPDS.find_furthest_from_mean(self.surface_values)
        assert isinstance(s_index, Number) and 0 <= s_index < len(self.surface_tris) , \
            "Surface index is valid: "+str(s_index) + ". Known surfaces length: "+str(len(self.surface_tris)) \
            + "\n" + str(self.surface_tris)
        s_i = self.surface_values[s_index]

        # Distance of MeanValue to FurthestSurfaceValue
        d = float(np.mean(self.surface_values) - s_i)  # The increase intensity total, to be shared among hitting LEDs.
        assert type(d) is float, "The intensity difference amount can be positive or negative."

        # Find the leds that hit the front face of this surface.
        # Find the Lambertian score per tri-front-face hitting LED to surface Si.
        l_scores = TuneUsingIterativeRegressionPDS.get_lambertians_scores_for_given_led_indexes(led_vertices=self.led_vertices,
                                                                led_intensities=led_intensities,
                                                                tri=self.surface_tris[s_index])
        assert all([x >= 0 for x in l_scores]), "All Lambertian Lumens quantities (scores) should be zero or positive."

        # Apply the increase across the hitting LEDs, according to their impact on the surface value.
        total = np.sum(l_scores)
        assert total > 0, "Total score value should always be greater than 0. There should be no negative scores."
        for i in range(len(l_scores)):
            score = l_scores[i]

            # Calculate the percentage change for this LED, and apply the update to the LED's corresponding intensity value.
            percent = score / total
            update_score = percent * d
            self.led_intensities[i] += float(update_score)

        surfaces = get_surface_evaluations(self.surface_tris, self.led_vertices, intensities=self.led_intensities)
        std = np.std(surfaces) / len(self.led_vertices)
        return std, {'intensities':self.led_intensities, 'surfaces':surfaces}

    @staticmethod
    def get_lambertians_scores_for_given_led_indexes(led_vertices=None, led_intensities=None, tri=None):
        assert type(led_vertices) is list and len(led_vertices) > 0 and type(led_intensities) is list \
               and len(led_intensities) == len(led_vertices), \
            "Ensure LED data is correct and equal."

        res = [0.0] * len(led_vertices)
        for i in range(len(led_vertices)):
            led = led_vertices[i]
            intensity = led_intensities[i]
            score = helper_illuminance.do_surface_evaluation_single_LED(tri=tri, led=led, intensity=intensity)
            res[i] = score
        return res

    @staticmethod
    def find_furthest_from_mean(array):
        value = np.mean(array)
        return (np.abs(array - value)).argmax()


