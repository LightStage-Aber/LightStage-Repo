default_path = "../src/"
import sys
sys.path.insert(0, default_path)

from helpers.test_support_pipe_capture import captured_stdout
import unittest

from options import getPropertiesFile, get_parsed_commandline_options
import run


class Config:
    SKIP_SLOW_TESTS = False
    SKIP_CONTROL_TESTS = False
    SKIP_MONTE_CARLO_TESTS = False

class SetupEvaluator:

    def options(self, m, e):
        PARSE_OPTIONS, PARSE_ARGS = get_parsed_commandline_options()
        PARSE_OPTIONS.EVALUATION = m
        PARSE_OPTIONS.EVALUATION_METRIC_MODE = e
        PARSE_OPTIONS.TARGET_SHAPE = "../models/dome/dome_c.obj"

    def execute_get_first_match_from_stdout(self, match):
        with captured_stdout() as stdout:
            x = run.LightStageApp()
            x.main()
        output_strings = str(stdout.getvalue()).strip().split("\n")
        stdout.close()

        matchers = [match]
        lines = [s for s in output_strings if any(xs in s for xs in matchers)]
        res = lines[0].replace(match,"")
        return res


class SetupEvaluateSingleResultsFile(SetupEvaluator):

    def properties(self, output_path_prefix, result_filename, number_of_leds, indexes_are_important_HCD, use_support_access):
        getPropertiesFile("../properties/default.properties")['EvaluateSingleResultsFile']['results_file.csvfilename'] = result_filename
        getPropertiesFile("../properties/default.properties")['EvaluateSingleResultsFile']['results_file.results_output_file_path_prefix'] = output_path_prefix
        getPropertiesFile("../properties/default.properties")['EvaluateSingleResultsFile']['results_file.column_number'] = 3
        getPropertiesFile("../properties/default.properties")['EvaluateSingleResultsFile']['results_file.number_of_leds'] = number_of_leds

        getPropertiesFile("../properties/default.properties")['FrameModel']['frame.withsupportaccess'] = use_support_access
        getPropertiesFile("../properties/default.properties")['FrameModel']['frame.indexes_are_important'] = indexes_are_important_HCD

class GetActual(object):
    def __init__(self):
        self._test_output_path  = None
        self._file_path         = None

    def _get_actual(self, m=None, e=None, filename=None, n=None, indexes_are_important=None, support_access=None):
        x = SetupEvaluateSingleResultsFile()
        x.options(
            m=m,
            e=e
        )
        x.properties(
            output_path_prefix=  self._test_output_path,
            result_filename= self._file_path +str(filename),
            number_of_leds=n,
            indexes_are_important_HCD=str(indexes_are_important),
            use_support_access=str(support_access)
        )
        actual = x.execute_get_first_match_from_stdout("Finished with normalised standard deviation:")
        return float(actual)


class PLOSOneEXP(unittest.TestCase, GetActual):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual.__init__(self)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = "../results/Control_91-92_March2017/"

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_VAcc(self):
        actual = self._get_actual(m=2, e=3, filename="l91.csv", n=91, indexes_are_important=True, support_access=True)
        expected = 0.00340693210971
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_VNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="l92.csv", n=92, indexes_are_important=True, support_access=False)
        #print(actual)
        #sys.exit()
        expected = 0.000708533321995
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_OddNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="odds.csv", n=46, indexes_are_important=True, support_access=False)
        expected = 0.00429237121612
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_OddAcc(self):
        actual = self._get_actual(m=2, e=3, filename="odds44.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00762615128411
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_EvenNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="evens.csv", n=46, indexes_are_important=True, support_access=False)
        expected = 0.00429237121612
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_EvenAcc(self):
        actual = self._get_actual(m=2, e=3, filename="evens44.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00762615128411
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    @unittest.skipIf(Config.SKIP_SLOW_TESTS, "Skipping slow test..")
    def test_control_E10Acc(self):
        actual = self._get_actual(m=2, e=4, filename="edges_l3893.csv", n=3893, indexes_are_important=False, support_access=True)
        expected = 0.0116138656448
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    @unittest.skipIf(Config.SKIP_SLOW_TESTS, "Skipping slow test..")
    def test_control_E10NoAcc(self):
        actual = self._get_actual(m=2, e=4, filename="edges_l3991.csv", n=3991, indexes_are_important=False, support_access=False)
        expected = 0.00655570792577
        self.assertTrue(actual == expected)
        return actual


class PLOSOneEXP_MonteCarlo(unittest.TestCase, GetActual):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual.__init__(self)
        self._file_path = "../results/installed_aos+rod_July2016/"

    @unittest.skipIf(Config.SKIP_MONTE_CARLO_TESTS, "Skipping monte carlo test..")
    def test_monte_carlo_Inst(self):
        actual = self._get_actual(m=2, e=3, filename="installed.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00591398315505
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(Config.SKIP_MONTE_CARLO_TESTS, "Skipping monte carlo test..")
    def test_monte_carlo_Twkr(self):
        actual = self._get_actual(m=2, e=3, filename="tweaker.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00460301483137
        self.assertTrue(actual == expected)
        return actual



if __name__ == "__main__":
    # suite = unittest.TestLoader().loadTestsFromTestCase( PLOSOneEXP )
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )

    # suite = unittest.TestSuite(); suite.addTest(Control_Edge_Evaluations('test_edges_l3893_hard_coded_frame'))
    # suite = unittest.TestSuite(); suite.addTest(Control_Evaluations('test_control_l91_using_hardcodedAOSMappedDome_True_is_same_as_test_control_l91_using_hardcodedAOSMappedDome_False'))
    unittest.TextTestRunner(verbosity=3).run(suite)
