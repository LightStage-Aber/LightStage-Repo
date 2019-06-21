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
         tune.regression.threshold=0.005 [Range: >=0] - Threshold score to beat before terminating. (Stopping criteria 1)
         tune.regression.max_improvement_attemps_on_best_score=10 [Range: >=1] - Number of attempts to improve on the current best score before accepting that as the final score. (Stopping criteria 2)
         tune.debug=False [In: True or False] - Print progress of search evaluations to STDOUT.
     """
    def __init__(self, evaluator_func, update_func):
        self._evaluator_func = evaluator_func
        self._update_func = update_func
        self.__set_properties()

    def __set_properties(self):
        dict_properties = getPropertiesFile("../properties/default.properties")
        self.threshold = float(dict_properties['BrightnessControlTuner']['tune.regression.threshold'])
        self.max_iterations = int(dict_properties['BrightnessControlTuner']['tune.regression.max_improvement_attemps_on_best_score'])

        self.DEBUG = property_to_boolean(section="BrightnessControlTuner", key="tune.debug")

        assert isinstance(self.threshold, Number) and self.threshold >= 0.0, \
            "Residual error threshold should be positive float: " + str(self.threshold) + ". Type: "+str(type(self.threshold))
        assert isinstance(self.max_iterations, Number) and self.max_iterations >= 1, \
            "Max search iterations should be positive int: " + str(self.max_iterations) + ". Type: " + str(type(self.max_iterations))

    def start(self, start_data):
        _starting_score = None
        default_value = sys.maxsize
        data = start_data[:]

        current_minimum = _FindMinimum(value=default_value, data=data, count=0, rounds=None)
        rounds = 0
        while True:
            rounds += 1
            data = self._update_func(data)
            x = self._evaluator_func(data)
            _starting_score = x if _starting_score is None else _starting_score

            if self.DEBUG:
                print("Round: "+str(rounds)+") - IterativeRegression - Score (Std/Qty): "+str(x)+" - (Best Round:"+str(current_minimum.count)+", Since Best Round:"+str(rounds-current_minimum.count) + ", Best Score: " + str(current_minimum.value) +")")

            is_best = x < current_minimum.value
            if is_best:
                current_minimum = _FindMinimum(value=x, data=data, count=rounds, rounds=None)
            has_been_evaluated = current_minimum.value != default_value
            is_threshold_exceeded = x < self.threshold                                                          # Stopping criteria 1
            has_exceeded_max_iterations_on_this_value = (current_minimum.count + self.max_iterations) <= rounds # Stopping criteria 2
            if is_threshold_exceeded or (has_been_evaluated and has_exceeded_max_iterations_on_this_value):
                break
        best_value = current_minimum.value
        best_data = current_minimum.data
        best_count = current_minimum.count
        current_minimum = _FindMinimum(value=best_value, data=best_data, count=best_count, rounds=rounds)
        if self.DEBUG:
            print("Start Score: "+str(_starting_score)+" Improved Score from "+str(rounds)+" trials: "+str(best_value))

        return current_minimum



