import numpy as np
import sys

from options import *
import tuners


class Tuning():
    @staticmethod
    def selector(**kwargs):
        dict_properties = getPropertiesFile("../properties/default.properties")
        TUNE_MODE = int(dict_properties['Tune']['tune.mode'])

        orig_std = np.std(kwargs['surface_values'])
        std = np.std(kwargs['surface_values'])
        res = {}
        if TUNE_MODE == 1:
            x = tuners.TuneUsingSearch(**kwargs)
            res = x.search()
            print res
            # res = bh.res
            # res.lowest_optimization_result = bh.storage.get_lowest()
            # res.x = np.copy(res.lowest_optimization_result.x)
            # res.fun = res.lowest_optimization_result.fun
            # res.message = message
            # res.nit = i + 1
            print "The Tuned LED Intensities: " + str(res.x)
            print "The Original non-normalised standard deviation: " + str(orig_std)
            print "The Tuned non-normalised standard deviation: " + str(res.fun)
            print "The Num of LEDS: " + str(len(res.x))
            # print "The Tuned rounds completed: " + str(res)

        elif TUNE_MODE == 2:
            tune_threshold = float(dict_properties['Tune']['tune.regression.threshold'])
            max_iterations = int(dict_properties['Tune']['tune.regression.max_iterations'])

            x = tuners.TuneUsingIterativeRegressionPDS(threshold=tune_threshold,
                                                       max_iterations=max_iterations, **kwargs)
            res = x.search()
            #(std = std, std_norm = std_norm, surface_values = surface_values, intensities = intensities, rounds = rounds)
            # print ("Mapped Vertex Positions: "+str(self.mapped) if len(self.mapped) < 10 else "")
            print "The Tuned rounds completed: " + str(res.rounds)
            print "The Tuned LED Intensities: " + str(res.intensities)
            print "The Original normalised standard deviation: " + str(orig_std / len(res.intensities))
            print "The Tuned normalised standard deviation: " + str(res.std_norm)
            print "The Original non-normalised standard deviation: " + str(orig_std)
            print "The Tuned non-normalised standard deviation: " + str(res.std)
            print "The Num of LEDS: " + str(len(res.intensities))
        else:
            print(__file__ + " -> " + sys._getframe().f_code.co_name + "()")
            assert(False, "Invalid TUNE_MODE option selected. Exiting.")
            sys.exit()
        return res
