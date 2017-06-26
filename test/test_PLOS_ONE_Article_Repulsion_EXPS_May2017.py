default_path = "../src/"
import sys
sys.path.insert(0, default_path)

import unittest
from helpers.helper_evaluation_tuning_tester import GetActual_FromVertex
from helpers.helper_repulsion_tester import Load_Lettvin_RepulsionData


class _Config:
    SKIP_RAW_REPULSION_TESTS = False
    SKIP_VERTEX_REPULSION_TESTS = False
    SKIP_EDGE_REPULSION_TESTS = False


class PLOSOneEXP_Repulsion_LettvinOnly(unittest.TestCase, Load_Lettvin_RepulsionData, GetActual_FromVertex):
    """
    This test suite requires:
        -  Running 'extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py' to expand the default results CSV file output.

    The evaluation mode e7-9 produces an output CSV file containing important data. However, it does not output
    the Lettvin parameter values (J, N, R and min-R). These are extracted from the associated test's obj filename.
    """
    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual_FromVertex.__init__(self, *args, **kwords)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = "" # Leave blank. The full file path *must be* specified within the individual unit tests.
        self.__error_threshold  = 0.00000000000001
        self.__source_path = "../results/Lettvin_RangeTest_Lambertian_Standard_Deviation_Results_91Vertices_44LEDS_1000iterations_Feb2017/output_March19th2017.csv"

    def __load_Profile_Results(self, MAPPING_TYPE):
        Load_Lettvin_RepulsionData.__init__(self, self.__source_path, MAPPING_TYPE)

    def __is_similar(self, actual, expected):
        return abs(float(actual) - float(expected)) < self.__error_threshold

    def __do_full_test(self, e=None):
        c = 0
        for k in self._minimum_results:
            c += 1
            result = self._minimum_results[k]
            expected = result[0]
            filepath = result[1]
            actual = self._get_actual(m=2, e=e, filename=filepath, n="Not Applicable", indexes_are_important=False, support_access=True)
            test_passed = self.__is_similar(actual, expected)

            if not test_passed:
                print("Failed for comparison with error threshold: " + str(self.__error_threshold)
                      + "\nFor values: Actual:(" + str(actual) + " == " + str(expected) + "):Expected"
                      + "\nFor hex: Actual:(" + str(float.hex(actual)) + " == " + str(
                    float.hex(expected)) + "):Expected"
                      + "\nFor types: Actual:(" + str(type(actual)) + " == " + str(type(expected)) + "):Expected"
                      + "\nFor length: Actual:(" + str(len(str(actual))) + " == " + str(
                    len(str(expected))) + "):Expected"
                      + "\nFor file: " + str(filepath) + "\nFor config: " + str(k))

            print(str(c) + ". " + str(test_passed) + " for " + str(k))
            self.assertTrue(test_passed)

    @unittest.skipIf(_Config.SKIP_RAW_REPULSION_TESTS, "Skipping raw repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_Raw(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.RAW)
        self.__do_full_test(e=7)

    @unittest.skipIf(_Config.SKIP_VERTEX_REPULSION_TESTS, "Skipping vertex repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_VertexMountings(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.VERTEX)
        self.__do_full_test(e=8)

    @unittest.skipIf(_Config.SKIP_EDGE_REPULSION_TESTS, "Skipping edge repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_EdgeMountings(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.EDGE)
        self.__do_full_test(e=9)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)