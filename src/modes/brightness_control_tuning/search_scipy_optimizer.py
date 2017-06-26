from __future__ import division
from scipy.optimize import basinhopping
from numbers import Number

from options import property_to_number, property_to_boolean

class SearchScipyOptimize():
    """
    Handler class for searches using scipy.optimize.basinhopping using method: "L-BFGS-B"
    See: https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.basinhopping.html
    """
    def __init__(self, search_evaluation_function):
        self.f = search_evaluation_function
        self.__set_properties()

    def __set_properties(self):
        self._method="L-BFGS-B"

        self._niter         = property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.niter', vmin=0, vmax=None, vtype=int) #100
        self._niter_success = property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.niter_success', vmin=0, vmax=10, vtype=int) #1
        self._lower_bounds  = property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.lower_bounds', vmin=0.0, vmax=2.0, vtype=float) #0.5
        self._upper_bounds  = property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.upper_bounds', vmin=0.0, vmax=2.0, vtype=float) #1.5
        self._T             = property_to_number(section='BrightnessControlTuner', key='tune.scipy.basinhopping.t', vmin=0.0, vmax=2.0, vtype=float) #1.0
        self._disp          = property_to_boolean(section='BrightnessControlTuner', key='tune.scipy.basinhopping.disp')

    def start(self, seq_to_optimize):
        x0 = seq_to_optimize
        assert isinstance(x0, list) and len(x0) > 0 and all([isinstance(x, Number) for x in x0]),  \
            "Input sequence should be a list of type numbers.Number.\n"+\
            "Type: "+str(type(x0))+"\n"+\
            "Len: "+str(len(x0))+"\n"+\
            "Values: "+str(x0)+"\n"+\
            "Types: "+str( [isinstance(x, Number) for x in x0] )+"\n"
        # the bounds
        xmin = [self._lower_bounds]*len(x0)
        xmax = [self._upper_bounds]*len(x0)

        bounds = self.__get_bounds_for_L_BFGS_B(xmin, xmax)

        # use method L-BFGS-B because the problem is smooth and bounded
        minimizer_kwargs = dict(method=self._method, bounds=bounds)
        res = basinhopping(self.f, x0, niter=self._niter, T=self._T, niter_success=self._niter_success, disp=self._disp, minimizer_kwargs=minimizer_kwargs)
        return res

    def __get_bounds_for_L_BFGS_B(self, xmin, xmax):
        # rewrite the bounds in the way required by L-BFGS-B
        return [(low, high) for low, high in zip(xmin, xmax)]

