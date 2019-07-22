default_path = "../../src/"
import sys
sys.path.insert(0, default_path)

import unittest

from sequences import *
from data_3d import WaveFront

class _Config:
    SKIP_COUNTER = False
    SKIP_INTERVALS = False


class Test_BaseBaseGradientSequence(unittest.TestCase):
    """
        Test the basic sequence generator that uses individual lights as intervals.
    """


    @unittest.skipIf(_Config.SKIP_COUNTER, "Skipping test..")
    def test_first_sequence_at_loop_0_counter_is_1(self):
        """"""
        gs = BaseGradientSequence( [[1,2,3],[4,5,6],[7,8,9]], [1,1,1])
        l = gs.get_next_sequence()
        s,loop  =gs.get_sequence_number()
        actual = s
        expected = 1
        self.assertTrue(actual == expected)

    @unittest.skipIf(_Config.SKIP_COUNTER, "Skipping test..")
    def test_first_sequence_at_loop_1_counter_is_1(self):
        """"""
        leds = [[1,2,3],[4,5,6],[7,8,9]]
        gs = BaseGradientSequence( leds, [1,2,3])
        
        for i in leds:
            l = gs.get_next_sequence()
            s,loop  = gs.get_sequence_number()
        l = gs.get_next_sequence()
        s,loop  = gs.get_sequence_number()
        actual = s
        expected = 1
        self.assertTrue(actual == expected)

    @unittest.skipIf(_Config.SKIP_INTERVALS, "Skipping test..")
    def test_output_intensities_intervals_starts_as_defined(self):
        """"""
        gs = BaseGradientSequence( [[1,2,3],[4,5,6],[7,8,9]], [1,1,1])
        l = gs.get_next_sequence()
        gradient_intensities = [ c.get_intensity() for c in l ]
        I = gradient_intensities
        actual = gradient_intensities[0]
        expected = gs.from_value
        sys.stderr.write(str(gradient_intensities)+" ... ")
        sys.stderr.write(str(actual)+" ... ")
        sys.stderr.write(str(expected)+" ... ")
        self.assertTrue(actual == expected)

    @unittest.skipIf(_Config.SKIP_INTERVALS, "Skipping test..")
    def test_output_intensities_intervals_ends_as_defined(self):
        """"""
        gs = BaseGradientSequence( [[1,2,3],[4,5,6],[7,8,9]], [1,1,1])
        l = gs.get_next_sequence()
        gradient_intensities = [ c.get_intensity() for c in l ]
        end_i = len(gradient_intensities)-1
        actual = gradient_intensities[end_i]
        sys.stderr.write(str(gradient_intensities)+" ... ")
        sys.stderr.write(str(actual)+" ... ")
        expected = gs.to_value
        sys.stderr.write(str(expected)+" ... ")
        self.assertTrue(actual == expected)

    @unittest.skipIf(_Config.SKIP_INTERVALS, "Skipping test..")
    def test_output_intensities_are_monotonic_for_given_set(self):
        """ """
        gs = BaseGradientSequence( [[1,2,3],[4,5,6],[7,8,9]], [1,1,1])
        l = gs.get_next_sequence()
        gradient_intensities = [ c.get_intensity() for c in l ]
        sys.stderr.write(str(gradient_intensities)+" ... ")
        I = gradient_intensities
        monotonic = [x>=y for x, y in zip(I, I[1:])]
        sys.stderr.write(str(monotonic)+" ... ")
        actual = all( monotonic )   # Monotonically increasing or equal. (non-strict)
        expected = True
        self.assertTrue(actual == expected)




class Test_GradientSequence_IntervalSpecified(unittest.TestCase):

    def test_first_sequence_at_loop_1_counter_is_1_on_real_data(self):
        leds = WaveFront.get_hardcoded_frame( scale=8 )
        intens = [1.0]*len(leds)
        intervals = 10
        gs = GradientSequence_IntervalSpecified( leds , intens , intervals )
        
        for i in range(intervals):
            l = gs.get_next_sequence()
            s,loop  = gs.get_sequence_number()

        l = gs.get_next_sequence()
        s,loop  = gs.get_sequence_number()
        actual = s
        expected = 1
        self.assertTrue(actual == expected)

    @staticmethod
    def _helper_check_monotonic(leds):
        gs = GradientSequence_IntervalSpecified( leds, len(leds)*[1], len(leds) )
        l = gs.get_next_sequence()
        gradient_intensities = [ c.get_intensity() for c in l ]
        # sys.stderr.write(str(gradient_intensities)+" ... ")
        I = gradient_intensities
        monotonic = [x<=y for x, y in zip(I, I[1:])]
        return monotonic

    def test_output_intensities_are_monotonic_for_given_dataset_from_negative_to_positive(self):
        """ """
        leds = zip( range(-8,9,1), range(-8,9,1), range(-8,9,1) )
        monotonic = Test_GradientSequence_IntervalSpecified._helper_check_monotonic( leds )
        # sys.stderr.write(str(monotonic)+" ... ")
        actual = all( monotonic )   # Monotonically increasing or equal. (non-strict)
        expected = True
        self.assertTrue(actual == expected)

    def test_output_intensities_are_monotonic_for_given_dataset_all_positive(self):
        """ """
        leds = zip( range(20),range(20),range(20) )
        monotonic = Test_GradientSequence_IntervalSpecified._helper_check_monotonic( leds )
        # sys.stderr.write(str(monotonic)+" ... ")
        actual = all( monotonic )   # Monotonically increasing or equal. (non-strict)
        expected = True
        self.assertTrue(actual == expected)

    def test_output_intensities_are_monotonic_after_rotation(self):
        """ """
        leds = zip( range(20),range(20),range(20) )
        gs = GradientSequence_IntervalSpecified( leds, len(leds)*[1], 3 )
        res = []
        for i in range(5):
            l = gs.get_next_sequence()
            gradient_intensities = [ c.get_intensity() for c in l ]
            # sys.stderr.write(str(gradient_intensities)+" ... ")
            I = gradient_intensities
            monotonic = [x<=y for x, y in zip(I, I[1:])]    # Monotonically increasing or equal. (non-strict)
            # sys.stderr.write(str(monotonic)+" ... ")
            is_mono_or_is_rotated_mono = all( monotonic ) or monotonic.count(False) == 1  
            # Only one position is non-monotonic, before and after which monotonicity will persist. 
            # This is the point at which rotation has caused the maximum value to rotate from start to a non-start position.
            res += [ is_mono_or_is_rotated_mono ]

        actual = all(res)
        expected = True
        self.assertTrue(actual == expected)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
