from __future__ import division
from abc import ABCMeta
from options import *
from file_utils import *
from manipulate_results_data import *
from visualisations import *

import random as rnd
import time;     currentMillis = lambda: int(round(time.time() * 1000))




class Evaluator():
    """
    Abstract Base Class (ABC) for LED position optimsation evaluators.
    """
    __metaclass__ = ABCMeta
    def __init__(self):
        """
        Construct evaluator object.
        """
    def evaluate(self):
        """
        Evaluate 
        """
