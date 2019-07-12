default_path = "../src/"
import sys
sys.path.insert(0, default_path)
import unittest
from helpers.helper_brightness_control_tuning_tester import BrightnessControlTuningTester


class _Config:
    SKIP_SLOW_ITERATIVE_REGRESSION_MONTE_CARLO_TESTS = False
    SKIP_ITERATIVE_REGRESSION_MONTE_CARLO_TESTS = True


class Test_IterativeRegression(unittest.TestCase, BrightnessControlTuningTester):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        BrightnessControlTuningTester.__init__(self, *args, **kwords)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = ""

    @unittest.skipIf(_Config.SKIP_ITERATIVE_REGRESSION_MONTE_CARLO_TESTS, "Skipping Monte Carlo iterative regression test..")
    def test_brightness_control_std_reduces_evaluation_std_on_MonteCarlo_InstalledCSV(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=3, filename="../results/installed_aos+rod_July2016/installed.csv", n=44, indexes_are_important=True, support_access=False)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_ITERATIVE_REGRESSION_MONTE_CARLO_TESTS, "Skipping Monte Carlo iterative regression test..")
    def test_brightness_control_std_reduces_evaluation_std_on_MonteCarlo_TweakerCSV(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=3, filename="../results/installed_aos+rod_July2016/tweaker.csv", n=44, indexes_are_important=True, support_access=False)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_ITERATIVE_REGRESSION_MONTE_CARLO_TESTS, "Skipping Monte Carlo iterative regression test..")
    def test_brightness_control_MonteCarlo_TweakerCSV__BetterThan_VAccControl(self):
        actual_std, actual_tuned = self._tune_IterativeRegression_SetThreshold(e=3, filename="../results/installed_aos+rod_July2016/tweaker.csv", n=44, indexes_are_important=True, support_access=False, threshold=0.00340693210971)
        self.assertTrue(actual_std > actual_tuned)





if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
