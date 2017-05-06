from scipy_optimize_wrapper import *

def test_evenness():
    led_vertices=[[-6.805208, 3.577712, -2.211144], [0.0, -6.357232, -4.856496], [0.0, 6.357232, 4.856496], [2.611816, -4.119344, 6.341088], [2.611816, 4.119344, -6.341088], [-6.805208, -3.577712, 2.211144], [7.835456, 1.373112, -0.848632]]
    led_intensities=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    surface_tris=[[[0.0, 0.0, 0.78], [0.45, 0.45, 0.0], [0.45, -0.45, 0.0]], [[0.0, 0.0, 0.78], [0.45, -0.45, 0.0], [-0.45, -0.45, 0.0]], [[0.0, 0.0, 0.78], [-0.45, -0.45, 0.0], [-0.45, 0.45, 0.0]], [[0.0, 0.0, 0.78], [-0.45, 0.45, 0.0], [0.45, 0.45, 0.0]], [[0.0, 0.0, -0.78], [-0.45, 0.45, 0.0], [-0.45, -0.45, 0.0]], [[0.0, 0.0, -0.78], [-0.45, -0.45, 0.0], [0.45, -0.45, 0.0]], [[0.0, 0.0, -0.78], [0.45, -0.45, 0.0], [0.45, 0.45, 0.0]], [[0.0, 0.0, -0.78], [0.45, 0.45, 0.0], [0.0, 0.0, 0.78]], [[0.0, 0.0, -0.78], [0.0, 0.0, 0.78], [-0.45, 0.45, 0.0]]]
    surface_center_vertices=[(0.29999999999999999, 0.0, 0.26000000000000001), (0.0, -0.29999999999999999, 0.26000000000000001), (-0.29999999999999999, 0.0, 0.26000000000000001), (0.0, 0.29999999999999999, 0.26000000000000001), (-0.29999999999999999, 0.0, -0.26000000000000001), (0.0, -0.29999999999999999, -0.26000000000000001), (0.29999999999999999, 0.0, -0.26000000000000001), (0.14999999999999999, 0.14999999999999999, 0.0), (-0.14999999999999999, 0.14999999999999999, 0.0)]
    surface_values=[2.0240200345939976, 2.0880925491829285, 1.9586180365085553, 1.3857812801005727, 1.861947994900432, 1.5295599156177557, 2.0240200345939976, 1.729908590994156, 1.9014684169136076]

    # the starting point
    x0 = led_intensities
    obj = Evenness_Metric(led_vertices=led_vertices,
                          led_intensities=led_intensities,
                          surface_tris=surface_tris,
                          surface_center_vertices=surface_center_vertices,
                          surface_values=surface_values)
                          
    minimise = SearchScipyOptimize(obj.evaluate)
    res = minimise.start( x0 )
    print res


class Search_Evaluator_Stdev_Sample(SearchEvaluator):
    def __init__(self, seed=None):
        super(SearchEvaluator, self).__init__()  # call super
        self.abc = 0.1
        import random as r
        self.r = r.Random()
        self.r.seed(seed)

    def evaluate(self, x):
        x[self.r.randint(0, len(x) - 1)] += self.abc
        return np.std(x)

def test_std_sample():
    # the starting point
    x0 = [10., 10.,9.,2.0,8.0]
    obj = Search_Evaluator_Stdev_Sample( seed=2 )                      
    minimise = SearchScipyOptimize(obj.evaluate)
    
    res = minimise.start( x0 )
    print res
    # Note: can't make assertions on result or final function evaluation of result, because Scipy shares, uses and reseeds the random object.


if __name__ == "__main__":
    #test_std_sample()
    test_evenness()
