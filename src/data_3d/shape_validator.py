from __future__ import division
import numpy as np
import sys


def checkShapeValidity( triangles ):
    """
    Ensure all triangles (2d list) contain exactly 3 float type values.
    """
    d = np.array(triangles).flat
    try:
        l = [float(x) for x in list(d)]
        is_invalid_type = False
    except ValueError as e:
        is_invalid_type = True
    is_invalid_length = [len(x) != 3 for x in triangles]
    
    if is_invalid_type:
        print("Aborting: Invalid tri value type in target shape.")
        sys.exit()
    if any(is_invalid_length):
        print("Lengths: ",is_invalid_length)
        print("Aborting: Invalid tri length in target shape.")
        sys.exit()

def checkVerticesValidity( vertices ):
    """
    Ensure all vertices (2d list) contain exactly 3 float type values.
    """
    d = np.array(vertices).flat
    try:
        l = [float(x) for x in list(d)]
        is_invalid_type = False
    except ValueError as e:
        is_invalid_type = True
    is_invalid_length = [len(x) != 3 for x in vertices]
    
    if is_invalid_type:
        print("Aborting: Invalid vertex coordinate value type.")
        sys.exit()
    if any(is_invalid_length):
        print("Lengths: ",is_invalid_length)
        print("Aborting: Invalid vertex coordinate length.")
        sys.exit()


