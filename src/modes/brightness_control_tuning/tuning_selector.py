from collections import namedtuple

from options import property_to_string
import tuners


class TuningInputDataContainer(namedtuple('_A', ['surface_tris', 'led_vertices', 'intensities'])):
    pass
class TuningOutputDataContainer(namedtuple('_A', ['intensities', 'surface_scores'])):
    pass


class BrightnessControlStrategy(object):
    """
    A strategy selector class for brightness control tuning stategies.

    ** Requires properties file configuration contains a valid "tune.mode="

    [BrightnessControlTuner]
    tune.mode=abc

    For example:
        tune.mode=L-BFGS-B
        tune.mode=IterativeRegression
    """

    def selector(self, input_container = None):

        brightness_control_tuning_strategy = property_to_string(section='BrightnessControlTuner', key='tune.mode').replace("\"","")
        kwargs = {}
        switcher = {
            "L-BFGS-B": tuners.TuneUsingScipyMinimize(**kwargs),
            "IterativeRegression": tuners.TuneUsingIterativeRegressionPDS(**kwargs)
        }
        tool = switcher.get(brightness_control_tuning_strategy, None)
        assert tool is not None, "Missing a valid Brightness Control stretegy. See option given in properties file configuration:\n" \
                                 "tune.mode="+str(brightness_control_tuning_strategy)

        output_container = tool.search( input_container ) if tool != None else None
        assert output_container is not None, "Missing result data from Brightness Control stretegy. See option given in properties file configuration:\n" \
                                 "tune.mode=" + str(brightness_control_tuning_strategy)

        return output_container

