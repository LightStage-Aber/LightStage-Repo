from __future__ import division
from collections import deque
import math
import numpy as np

### Calculate X-Axis Gradient White Value.
class BaseSequenceContainer:
    def __init__(self, led_vertex, x_value, index, intensity_baseline):
        self.led_vertex = led_vertex
        self.x_value = x_value
        self.index = index
        
        self.intensity_baseline = intensity_baseline
        self.intensity_gradient = None
        
    def apply_gradient(self, f) :
        self.intensity_gradient = f

    def get_index(self):
        return self.index

    def get_intensity(self):
        assert self.intensity_baseline is not None and self.intensity_gradient is not None , "LED index at "+str(self.index)+": baseline intensity, gradient intensity or proportional (rotation) position have not been set."
        return self.intensity_baseline * self.intensity_gradient #watch out for accumulated/ power loss, e.g. when 0.5*0.5. Max values should be rescaled up to 1.0 (full) wattage.


class BaseGradientSequence:
    """
        The basic sequence generator uses individual lights as intervals. 
            - This causes a quantity of sequence lighting steps equal to number of lights, which has a very specific and lengthy use case.

        Public methods:
            get_next_sequence()
            get_sequence_number()
            __init__()
    """

    def __init__(self, leds_vertices, intensity_baselines, axis="x", scaled_range=[0.5, 1.0]):
        self.leds_vertices = leds_vertices
        self.intensity_baselines = intensity_baselines
        self.from_value = scaled_range[1] #1.0
        self.to_value = scaled_range[0] #0.5
        self.axis = ord(axis)-120 if axis in ["x","y","z"] else None # Default to assertion failure.
        self.loop_number = 0
        self.sequence_counter = 0
        assert self.axis in [0,1,2], "`Axis` argument must be specified as either \"x\", \"y\" or \"z\"."
        assert self.leds_vertices is not None and self.intensity_baselines is not None, "Requires led vertex and corresponding intensity data in a sequence data type."
        assert len(self.intensity_baselines) == len(self.leds_vertices), "The quantities of LED vertices and Intensity Baselines should be identical."
        assert self.from_value > self.to_value, "From value (e.g. 1.0) should be larger than To value (e.g. 0.5)." 
        self.dequeue_Ls = self.__initialise()
        
    def __initialise(self):
        self.dequeue_Ls = []
        self.__collect()
        self.__order_by_axis()
        self.dequeue_Ls = deque(self.dequeue_Ls)
        return self.dequeue_Ls

    def __collect(self):
        if len(self.dequeue_Ls) == 0: # Avoid repeated processing for a collection.
            for i in range(len(self.leds_vertices)):
                vertex = self.leds_vertices[i]
                intensity = self.intensity_baselines[i]
                c = BaseSequenceContainer( vertex, vertex[self.axis], i, intensity )
                self.dequeue_Ls.append( c ) 
        return self.dequeue_Ls

    def __order_by_axis(self):
        self.dequeue_Ls.sort( key=lambda c: c.x_value )

    def __apply_gradient(self):
        interval = self.__get_interval()
        curr_interval = self.from_value
        for i in range(len(self.dequeue_Ls)):
            L = self.dequeue_Ls[i]
            L.apply_gradient( curr_interval )
            curr_interval -= interval

    def __get_interval(self):
        grad_range = self.from_value-self.to_value
        interval = grad_range / (len(self.dequeue_Ls)-1)
        return interval

    def __rotate(self):
        Ls = self.dequeue_Ls
        end = self.dequeue_Ls.pop()       # Pop end (right).
        self.dequeue_Ls.appendleft( end ) # Insert end at start (left).
        
    def get_sequence_number(self):
        return self.sequence_counter, self.loop_number
 
    def get_next_sequence(self):
        def __handle_sequence_count():
            # handle index wrap around. Max = len(Ls) 
            if self.sequence_counter == len(self.dequeue_Ls): # Reached end of loop, therefore reset/update counters.
                self.loop_number += 1
                self.sequence_counter = 1
            else:                                               # start or midway through loop, update counter.
                self.sequence_counter +=1
        
        if self.sequence_counter is 0 and self.loop_number is 0: # First ever call
            self.__apply_gradient()
        else:                                                    # All subsequent calls
            self.__rotate()
            self.__apply_gradient()
        
        __handle_sequence_count()

        return self.dequeue_Ls



class GradientSequence_IntervalSpecified(BaseGradientSequence):
    """
        The Interval Specified Sequence Generator uses specified quantity of intervals lighting steps, proportionally illuminated based on X-axis position. 
            - The quantity of sequence lighting steps is specified by user.

        Public methods:
            get_next_sequence()
            get_sequence_number()
            __init__()
    """

    def __init__(self, leds_vertices, intensity_baselines,  axis="x", scaled_range=[0.5, 1.0], quantity_of_intervals=10):
        BaseGradientSequence.__init__(self, leds_vertices, intensity_baselines, axis, scaled_range)
        self.quantity_of_intervals = quantity_of_intervals
        assert leds_vertices is not None and isinstance(leds_vertices, list) and len(leds_vertices) > 0, "Sequence LED vertices must be valid, list type and quantity GT 0."
        assert intensity_baselines is not None and isinstance(intensity_baselines, list) and len(intensity_baselines) > 0, "Sequence LED intensities must be valid, list type and quantity GT 0."
        assert self.quantity_of_intervals > 0, "Quantity intervals ({}) must be GT 0.".format(self.quantity_of_intervals)
        assert self.quantity_of_intervals <= len(leds_vertices), "Quantity intervals ({},({})) must be LTEQ quantity of lights ({},({})), result is {}.".format(
                                                                                    self.quantity_of_intervals, type(self.quantity_of_intervals),
                                                                                    len(leds_vertices), type(len(leds_vertices)),
                                                                                    (self.quantity_of_intervals <= len(leds_vertices)))

    

    def __apply_gradient(self):
        def __renormalize(n, range1=[0.0,1.0]):
            delta1 = max(n) - min(n)
            delta2 = range1[1] - range1[0]
            return (delta2 * (np.array(n) - min(n)) / delta1) + range1[0]
        def __get_proportion_list():
            x_axis = [ c.x_value for c in self.dequeue_Ls ]
            proportions = __renormalize(x_axis) # 2a. proportional positions , scale above 0.
            assert all( [ 0.0 <= x <= 1.0 for x in proportions ] ), "Proportions should be between 0.0 and 1.0 only. Found: "+str(proportions)
            assert all( [ c.x_value == x for c,x in zip( self.dequeue_Ls, x_axis ) ] ), "Proportions list and dequeue_Ls list should remain in identical order to maintain trackability."
            gradients = __renormalize(proportions, range1=[self.to_value, self.from_value])
            assert all( [ self.to_value <= x <= self.from_value for x in gradients ] ), "Gradients should be between "+str(self.to_value)+" and "+str(self.to_value)+" only. Found: "+str(gradients)            
            return gradients
        props = __get_proportion_list() # 2a. proportional positions (as ratio)
        for i in range(len(self.dequeue_Ls)):  
            c = self.dequeue_Ls[i]
            p = props[i]
            c.apply_gradient(p)

    def __rotate(self):
        steps = int( math.floor(len(self.dequeue_Ls) / self.quantity_of_intervals) )
        for i in range( steps ):
            
            end = self.dequeue_Ls.pop()       # Pop end (right).
            self.dequeue_Ls.appendleft( end ) # Insert end at start (left).

        
    def get_next_sequence(self):
        def __handle_sequence_count():
            # handle index wrap around. Max = len(Ls) 
            if self.sequence_counter == self.quantity_of_intervals: # Reached end of loop, therefore reset/update counters.
                self.loop_number += 1
                self.sequence_counter = 1
            else:                                               # start or midway through loop, update counter.
                self.sequence_counter +=1
        
        if self.sequence_counter is 0 and self.loop_number is 0: # First ever call
            self.__apply_gradient()
        else:                                                    # All subsequent calls
            self.__rotate()
            self.__apply_gradient()
        
        __handle_sequence_count()

        return self.dequeue_Ls