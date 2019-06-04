default_path = "../src/"
import sys
sys.path.insert(0, default_path)
import unittest
from helpers.helper_evaluation_tuning_tester import GetActual_FromIndex


class _Config:
    SKIP_SLOW_TESTS = True
    SKIP_CONTROL_TESTS = False
    SKIP_MONTE_CARLO_TESTS = False


class PLOSOneEXP_Controls(unittest.TestCase, GetActual_FromIndex):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual_FromIndex.__init__(self)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = "../results/Control_91-92_March2017/"

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_VAcc(self):
        actual = self._get_actual(m=2, e=3, filename="l91.csv", n=91, indexes_are_important=True, support_access=True)
        expected = 0.00340693210971
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_VNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="l92.csv", n=92, indexes_are_important=True, support_access=False)
        expected = 0.000708533321995
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_OddNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="odds.csv", n=46, indexes_are_important=True, support_access=False)
        expected = 0.00429237121612
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_OddAcc(self):
        actual = self._get_actual(m=2, e=3, filename="odds44.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00762615128411
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_EvenNoAcc(self):
        actual = self._get_actual(m=2, e=3, filename="evens.csv", n=46, indexes_are_important=True, support_access=False)
        expected = 0.00429237121612
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_CONTROL_TESTS, "Skipping control test..")
    def test_control_EvenAcc(self):
        actual = self._get_actual(m=2, e=3, filename="evens44.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00762615128411
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_SLOW_TESTS, "Skipping slow test..")
    def test_control_E10Acc(self):
        actual = self._get_actual(m=2, e=4, filename="edges_l3893.csv", n=3893, indexes_are_important=False, support_access=True)
        expected = 0.0116138656448
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_SLOW_TESTS, "Skipping slow test..")
    def test_control_E10NoAcc(self):
        actual = self._get_actual(m=2, e=4, filename="edges_l3991.csv", n=3991, indexes_are_important=False, support_access=False)
        expected = 0.00655570792577
        self.assertTrue(actual == expected)
        return actual


class PLOSOneEXP_MonteCarlo(unittest.TestCase, GetActual_FromIndex):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual_FromIndex.__init__(self)
        self._file_path = "../results/installed_aos+rod_July2016/"

    @unittest.skipIf(_Config.SKIP_MONTE_CARLO_TESTS, "Skipping monte carlo test..")
    def test_monte_carlo_Inst(self):
        actual = self._get_actual(m=2, e=3, filename="installed.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00591398315505
        self.assertTrue(actual == expected)
        return actual

    @unittest.skipIf(_Config.SKIP_MONTE_CARLO_TESTS, "Skipping monte carlo test..")
    def test_monte_carlo_Twkr(self):
        actual = self._get_actual(m=2, e=3, filename="tweaker.csv", n=44, indexes_are_important=True, support_access=False)
        expected = 0.00460301483137
        self.assertTrue(actual == expected)
        return actual


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)