from __future__ import division
from numbers import Number
from collections import namedtuple
import sys

from options import getPropertiesFile, property_to_boolean


class _FindMinimum(namedtuple('FindMinimum', ['value', 'data', 'count', 'rounds'])):
    pass


class IterativeRegression():
    """
     Class to perform tuning using an iterative regression to reduce surface illumination standard deviation.

     The approach iteratively updates LED intensities that affect the surface triangle with the illumination score
     furthest from mean, until the normalised standard deviation error threshold is reached; i.e. the residual error
     falls below the desired threshold.

     This is greedy (best-first) limited local optimsation. It uses the following properties file parameters.

         [BrightnessControlTuner]
         tune.regression.threshold=0.005 [Range: >=0]
         tune.regression.max_iterations=100 [Range: >=1]
         tune.regression.debug=False [In: True or False]
     """
    def __init__(self, evaluator_func, update_func):
        self._evaluator_func = evaluator_func
        self._update_func = update_func
        self.__set_properties()

    def __set_properties(self):
        dict_properties = getPropertiesFile("../properties/default.properties")
        self.threshold = float(dict_properties['BrightnessControlTuner']['tune.regression.threshold'])
        self.max_iterations = int(dict_properties['BrightnessControlTuner']['tune.regression.max_iterations'])

        self.DEBUG = property_to_boolean(section="BrightnessControlTuner", key="tune.regression.debug")

        assert isinstance(self.threshold, Number) and self.threshold >= 0.0, \
            "Residual error threshold should be positive float: " + str(self.threshold) + ". Type: "+str(type(self.threshold))
        assert isinstance(self.max_iterations, Number) and self.max_iterations >= 1, \
            "Max search iterations should be positive int: " + str(self.max_iterations) + ". Type: " + str(type(self.max_iterations))

    def start(self, start_data):
        default_value = sys.maxsize
        data = start_data[:]

        current_minimum = _FindMinimum(value=default_value, data=data, count=0, rounds=None)
        rounds = 0
        while True:
            rounds += 1
            data = self._update_func(data)
            x = self._evaluator_func(data)

            if self.DEBUG:
                print(str(rounds)+") Score: "+str(x)+" - (r"+str(current_minimum.count)+"/"+str(rounds-current_minimum.count) + " Best: " + str(current_minimum.value) +")")

            is_best = x < current_minimum.value
            if is_best:
                current_minimum = _FindMinimum(value=x, data=data, count=rounds, rounds=None)
            has_been_evaluated = current_minimum.value != default_value
            has_exceeded_max_iterations_on_this_value = (current_minimum.count + self.max_iterations) <= rounds
            is_threshold_exceeded = x < self.threshold
            if is_threshold_exceeded or (has_been_evaluated and has_exceeded_max_iterations_on_this_value):
                break
        best_value = current_minimum.value
        best_data = current_minimum.data
        best_count = current_minimum.count
        current_minimum = _FindMinimum(value=best_value, data=best_data, count=best_count, rounds=rounds)

        return current_minimum



