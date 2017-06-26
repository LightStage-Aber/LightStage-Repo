default_path = "../src/"
import sys
sys.path.insert(0, default_path)
import unittest
from helpers.helper_brightness_control_tuning_tester import BrightnessControlTuningTester


class _Config:
    SKIP_SLOW_ITERATIVE_REGRESSION_TESTS = True
    SKIP_SLOW_SCIPY_BASINHOPPING_TESTS = True
    SKIP_ITERATIVE_REGRESSION_TESTS = False
    SKIP_SCIPY_BASINHOPPING_TESTS = False


class Test_IterativeRegression(unittest.TestCase, BrightnessControlTuningTester):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        BrightnessControlTuningTester.__init__(self, *args, **kwords)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = ""

    @unittest.skipIf(_Config.SKIP_ITERATIVE_REGRESSION_TESTS, "Skipping iterative regression test..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedIndexes_ToVertex(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=3, filename="../results/Control_91-92_March2017/odds.csv", n=46, indexes_are_important=True, support_access=False)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_ITERATIVE_REGRESSION_TESTS, "Skipping slow iterative regression test.. this one has many led positions to check..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedIndexes_ToEdge(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=4, filename="../results/Control_91-92_March2017/edges_l3893.csv", n=3893, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_ITERATIVE_REGRESSION_TESTS, "Skipping slow iterative regression test.. this position set, by design, is already close to perfect with brightness control equally balanced.. ")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToRaw(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=7, filename="../results/Sample_Lettvin_Results_Mar2017/result_diffuse_positions_n44_j0.0000001_r0_i1__2017-03-18_05-02.txt.obj", n=44, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_ITERATIVE_REGRESSION_TESTS, "Skipping iterative regression test..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToVertex(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=8, filename="../results/Sample_Lettvin_Results_Mar2017/result_diffuse_positions_n44_j0.0000001_r0_i1__2017-03-18_05-02.txt.obj", n=44, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_ITERATIVE_REGRESSION_TESTS, "Skipping iterative regression test..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToEdge(self):
        actual_std, actual_tuned = self._tune_IterativeRegression(e=9, filename="../results/Sample_Lettvin_Results_Mar2017/result_diffuse_positions_n44_j0.0000001_r0_i1__2017-03-18_05-02.txt.obj", n=44, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)


class Test_SciPyBasinHopping(unittest.TestCase, BrightnessControlTuningTester):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        BrightnessControlTuningTester.__init__(self, *args, **kwords)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = ""

    @unittest.skipIf(_Config.SKIP_SCIPY_BASINHOPPING_TESTS, "Skipping scipy basin hopping test..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedIndexes_ToVertex(self):
        actual_std, actual_tuned = self._tune_SciPyBasinHopping(e=3, filename="../results/Control_91-92_March2017/l10s.csv", n=10, indexes_are_important=True, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_SCIPY_BASINHOPPING_TESTS,"Skipping slow scipy basin hopping test.. this one has many led positions to check..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedIndexes_ToEdges(self):
        actual_std, actual_tuned = self._tune_SciPyBasinHopping(e=4, filename="../results/Control_91-92_March2017/edges_l10s.csv", n=11, indexes_are_important=True, support_access=False)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_SCIPY_BASINHOPPING_TESTS, "Skipping slow scipy basin hopping test.. this position set, by design, is already close to perfect with brightness control equally balanced.. ")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToRaw(self):
        actual_std, actual_tuned = self._tune_SciPyBasinHopping(e=7, filename="../results/Sample_Lettvin_Results_Mar2017/test_tuning_n7_j0-001.txt.obj", n=7, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SCIPY_BASINHOPPING_TESTS, "Skipping scipy basin hopping test..")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToVertex(self):
        actual_std, actual_tuned = self._tune_SciPyBasinHopping(e=8, filename="../results/Sample_Lettvin_Results_Mar2017/test_tuning_n7_j0-001.txt.obj", n=7, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)

    @unittest.skipIf(_Config.SKIP_SLOW_SCIPY_BASINHOPPING_TESTS, "Skipping scipy basin hopping test.. (takes ~1.7hrs)")
    def test_brightness_control_std_reduces_evaluation_std_on_LoadedPositions_ToEdge(self):
        actual_std, actual_tuned = self._tune_SciPyBasinHopping(e=9, filename="../results/Sample_Lettvin_Results_Mar2017/test_tuning_n7_j0-001.txt.obj", n=7, indexes_are_important=False, support_access=True)
        self.assertTrue(actual_std > actual_tuned)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
