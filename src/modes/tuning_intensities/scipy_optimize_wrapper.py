from __future__ import division
from abc import ABCMeta
from scipy.optimize import basinhopping
from numbers import Number


class SearchScipyOptimize():
    """
    Handler class for searches using scipy.optimize.
    """
    def __init__(self, search_evaluation_function):
        self.f = search_evaluation_function
        
    def start(self, seq_to_optimize):
        x0 = seq_to_optimize
        assert isinstance(x0, list) and len(x0) > 0 and all([isinstance(x, Number) for x in x0]),  \
            "Input sequence should be a list of type numbers.Number."
        # the bounds
        xmin = [0.5]*len(x0)
        xmax = [1.5]*len(x0)

        # rewrite the bounds in the way required by L-BFGS-B
        bounds = [(low, high) for low, high in zip(xmin, xmax)]

        # use method L-BFGS-B because the problem is smooth and bounded
        minimizer_kwargs = dict(method="L-BFGS-B", bounds=bounds)
        res = basinhopping(self.f, x0, minimizer_kwargs=minimizer_kwargs)
        return res



class SearchEvaluator():
    """
    Abstract Base Class (ABC) for search evaluators.
    """
    __metaclass__ = ABCMeta
    def __init__(self):
        """
        constructor
        """
        
    def evaluate(self, x): 
        """
        
        """
        return 0.0

