from __future__ import division
import numpy as np
import sys

	
def euclidean_distance( v1, v2 ):
	"""
	Euclidean distance. (Using numpy for "fastest runtime").
	Source: http://stackoverflow.com/a/1401828/1910555
	Alternative distance measure implementations at https://docs.scipy.org/doc/scipy/reference/spatial.distance.html
	"""
	a = np.array(v1)
	b = np.array(v2)
	dist = np.linalg.norm(a-b)
	return dist
	

