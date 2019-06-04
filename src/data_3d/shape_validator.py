from __future__ import division
import numpy as np
import sys


def checkShapeValidity( polyfaces ):
    """
    Validates loaded:
        - data types as floats
        - ensures quantity of vertices is GTEQ 3
        - aborts (sys.exit()) program on failure.
    Input: `3d list` of polyfaces, of vertices and and final list of exactly 3 float type values.
    Return: void
    """
    d = np.array(polyfaces).flat
    try:
        l = [float(x) for x in list(d)]
        is_invalid_type = False
    except ValueError as e:
        is_invalid_type = True
    is_invalid_length = [len(x) < 3 for x in polyfaces]
    
    if is_invalid_type:
        print("Aborting: Invalid vertex (float-point) value type in target shape.")
        sys.exit()
    if any(is_invalid_length):
        print("Lengths: ",is_invalid_length)
        print("Aborting: Invalid poly-face vertex quantity in target shape. Expected GTEQ 3.")
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


