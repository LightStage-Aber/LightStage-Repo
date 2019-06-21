from __future__ import division
from numbers import Number
import numpy as np

from ..illuminance import helper_illuminance
from ..illuminance.helper_illuminance import get_surface_evaluations
from search_scipy_optimizer import SearchScipyOptimize
from tuning_selector import TuningInputDataContainer, TuningOutputDataContainer
from search_iterative_regression import IterativeRegression, _FindMinimum

from options import property_to_boolean

class AbstractTuner():
    """
        Abstract Tuner superclass.

        [BrightnessControlTuner]
        tune.debug=False [In: True or False]
    """
    def __init__(self):
        self.DEBUG = property_to_boolean(section="BrightnessControlTuner", key="tune.debug")

    def search(self, tuning_input_data_container):
        """Should execute and return search using input data."""
        raise NotImplementedError()

    def evaluate(self, x):
        """Should return evaluation score of 'x'."""
        raise NotImplementedError()

    def _get_extra_data(self, tuning_input_data_container):
        self._led_vertices = tuning_input_data_container.led_vertices
        self._surface_tris = tuning_input_data_container.surface_tris
        self._start_intensities = tuning_input_data_container.intensities
        self._surface_values = get_surface_evaluations(self._surface_tris, self._led_vertices, intensities=self._start_intensities)


class TuneUsingScipyMinimize(AbstractTuner):

    def search(self, tuning_input_data_container):
        self.__rounds = 0
        self._get_extra_data(tuning_input_data_container)
        minimise = SearchScipyOptimize(self.evaluate)
        res = minimise.start(self._start_intensities)
        return TuningOutputDataContainer(intensities = res.x, surface_scores = self._surface_values )

    def evaluate(self, data):
        self.__rounds += 1
        self._surface_values = get_surface_evaluations(self._surface_tris, self._led_vertices, intensities=data)
        normalised_std = np.std(self._surface_values) / len(self._start_intensities)
        if self.DEBUG:
            print("ScipyOptimize Eval Round: "+str(self.__rounds) + ") Score (Std/Qty): " + str(normalised_std) +" Intensities: [0-9]" + str(data[:10])+", Mean (Int): "+str(np.mean(data)) )
        return normalised_std


class TuneUsingIterativeRegressionPDS(AbstractTuner):

    def search(self, tuning_input_data_container):
        self.__rounds = 0
        self._get_extra_data(tuning_input_data_container)
        search_tool = IterativeRegression( self.evaluate, self.update )
        res = search_tool.start( self._start_intensities )
        return TuningOutputDataContainer(intensities = res.data, surface_scores = self._surface_values )

    def evaluate(self, data):
        self.__rounds += 1
        self._surface_values = get_surface_evaluations(self._surface_tris, self._led_vertices, intensities=data)
        normalised_std = np.std(self._surface_values) / len(self._led_vertices)
        if self.DEBUG:
            print("Round: "+str(self.__rounds) + ") - Evaluate() - Score (Std/Qty): " + str(normalised_std) +" Intensities: [0-4]" + str(data[:5])+", Mean (Int): "+str(np.mean(data)) )
        return normalised_std

    def update(self, data):
        index = self.__find_furthest_from_mean( self._surface_values )
        diff = self.__get_distance_to_mean(index)
        total, scores_per_leds = self.__get_current_scores(data, tri=self._surface_tris[index])
        updates = [self.__percentage_change(x, total, diff) for x in scores_per_leds]
        res = [data[i]+updates[i] for i in range(len(updates))]
        return res

    def __percentage_change(self, x, total, diff):
        # Apply the increase/decrease across the hitting LEDs, according to their impact on the surface value.
        return float((x / total) * diff)

    def __get_distance_to_mean(self, index):
        s_i = self._surface_values[index]
        # Distance of MeanValue to FurthestSurfaceValue
        d = float(np.mean(self._surface_values) - s_i)  # The increase intensity total, to be shared among hitting LEDs.
        assert type(d) is float, "The intensity difference amount can be positive or negative."
        return d

    def __get_current_scores(self, intensities=None, tri=None):
        # Find the Lambertian score per tri-front-face hitting LED to surface Si.
        res = [0.0] * len(self._led_vertices)
        for i in range(len(self._led_vertices)):
            res[i] = helper_illuminance.do_surface_evaluation_single_LED(tri=tri, led=self._led_vertices[i], intensity=intensities[i])
        assert all([l >= 0 for l in res]), "All Lambertian Lumen quantities (scores) should be zero or positive."
        total = np.sum(res)
        assert total > 0, "Total score value should always be greater than 0. There should be no negative scores."
        return total, res

    def __find_furthest_from_mean(self, values):
        # Find Surface_Value furthest from mean
        value = np.mean(values)
        index = (np.abs(values - value)).argmax()
        assert isinstance(index, Number) and 0 <= index < len(self._surface_tris), \
            "Surface index is valid: " + str(index) + ". Known surfaces length: " + str(
                len(self._surface_tris)) + "\n" + str(self._surface_tris)
        return index







