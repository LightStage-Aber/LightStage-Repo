import sys
default_path = "../src/"
sys.path.insert(0, default_path)
import unittest
from options import getPropertiesFile
from helper_evaluation_tuning_tester import GetActual_FromIndex

class _Config:
    DEBUG = True

class BrightnessControlTuningTester(GetActual_FromIndex):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual_FromIndex.__init__(self)

    def _tune_IterativeRegression_SetThreshold(self, e=None, filename=None, n=None, indexes_are_important=None, support_access=None, threshold=None):
        actual_std = threshold

        getPropertiesFile()['BrightnessControlTuner']['tune.mode'] = "IterativeRegression"
        getPropertiesFile()['BrightnessControlTuner']['tune.debug'] = False
        getPropertiesFile()['BrightnessControlTuner']['tune.regression.debug'] = False
        getPropertiesFile()['BrightnessControlTuner']['tune.regression.threshold'] = actual_std
        getPropertiesFile()['BrightnessControlTuner']['tune.regression.max_improvement_attempts_on_best_score'] = 8

        from time_utils.timer import MyTimer
        with MyTimer():
            actual_tuned = self._get_actual(m=3, e=e, filename=filename, n=n,
                                            indexes_are_important=indexes_are_important, support_access=support_access)
        if _Config.DEBUG:
            sys.stderr.write(str(actual_tuned)+" ... "+str(threshold)+" ... ")
        return actual_std, actual_tuned

    def _tune_IterativeRegression(self, e=None, filename=None, n=None, indexes_are_important=None, support_access=None):
        actual_std = self._get_actual(m=2, e=e, filename=filename, n=n, indexes_are_important=indexes_are_important, support_access=support_access)
        return self._tune_IterativeRegression_SetThreshold(e=e, filename=filename, n=n, indexes_are_important=indexes_are_important, support_access=support_access, threshold=actual_std)

    def _tune_SciPyBasinHopping(self, e=None, filename=None, n=None, indexes_are_important=None, support_access=None):
        actual_std = self._get_actual(m=2, e=e, filename=filename, n=n, indexes_are_important=indexes_are_important, support_access=support_access)
        getPropertiesFile()['BrightnessControlTuner']['tune.mode'] = "L-BFGS-B"

        getPropertiesFile()['BrightnessControlTuner']['tune.debug'] = False
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.niter'] = 0
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.niter_success'] = 1
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.lower_bounds'] = 0.5
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.upper_bounds'] = 1.5
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.t'] = 0.5
        getPropertiesFile()['BrightnessControlTuner']['tune.scipy.basinhopping.disp'] = False

        from time_utils.timer import MyTimer
        with MyTimer():
            actual_tuned = self._get_actual(m=3, e=e, filename=filename, n=n, indexes_are_important=indexes_are_important, support_access=support_access)

        if _Config.DEBUG:
            sys.stderr.write(str(actual_tuned)+" ... "+str(threshold)+" ... ")
        return actual_std, actual_tuned
