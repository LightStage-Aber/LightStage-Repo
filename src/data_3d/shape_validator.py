from __future__ import division
import numpy as np
import sys
from service import GracefulShutdown


def get_array_depth(L): 
    # depth = lambda L: isinstance(L, list) and max(map(depth, L))+1
    # return 0 if L is [] else depth(L)
    nparr = np.array(L)
    return len(nparr.shape)

def array_shape(L):
    nparr = np.array(L)
    return nparr.shape


def checkShapeValidity( polyfaces ):
    """
    Validates loaded:
        - data types as floats
        - ensures quantity of vertices is GTEQ 3
        - aborts program on failure.
    Input: `3d list` of polyfaces, of vertices and and final list of 3 or more float type values.
    Return: void
    """
    # print(array_shape(polyfaces))
    valid = True
    # __structure_depth = get_array_depth( polyfaces )
    # __expected_depth = 3
    # is_invalid_structure_depth = not (__structure_depth == __expected_depth)
    # d = np.array(polyfaces).flat
    # try:
    #     l = [float(x) for x in d]
    #     is_invalid_type = False
    # except ValueError as e:
    #     is_invalid_type = True
    # except TypeError as e:
    #     is_invalid_type = True
    is_invalid_length = [len(x) < 3 for x in polyfaces]
    
    # if is_invalid_structure_depth:
    #     print("Aborting: Invalid depth of shape data structure ([faces][vertex][float]). Actual: "+str(__structure_depth)+" Expected: "+str(__expected_depth))
    #     valid = False
    # if is_invalid_type:
    #     print("Aborting: Invalid vertex (float-point) value type in target shape.")
    #     valid = False
    if any(is_invalid_length):
        print("Lengths: ",is_invalid_length)
        print("Aborting: Invalid poly-face vertex quantity in target shape. Expected GTEQ 3.")
        valid = False
    if not valid:
        __invalid_obj_report( polyfaces, obj_component_type="shape" )


def checkFaceValidity( polyfaces ):
    """
    Validates loaded:
        - data types as ints
        - ensures quantity of vertices is GTEQ 3
        - aborts program on failure.
    Input: `3d list` of polyfaces, of vertices and and final list of 3 or more int type values.
    Return: void
    """
    # print(array_shape(polyfaces))
    valid = True
    __structure_depth = get_array_depth( polyfaces )
    __expected_depth = 2
    is_invalid_structure_depth = not (__structure_depth == __expected_depth)
    # d = np.array(polyfaces).flat
    # try:
    #     l = [int(x) for x in d]
    #     is_invalid_type = False
    # except ValueError as e:
    #     is_invalid_type = True
    # except TypeError as e:
    #     is_invalid_type = True
    is_invalid_length = [len(x) < 3 for x in polyfaces]
    
    if is_invalid_structure_depth:
        print("Aborting: Invalid depth of face data structure ([faces][vertex][float]). Actual: "+str(__structure_depth)+" Expected: "+str(__expected_depth))
        valid = False
    # if is_invalid_type:
    #     print("Aborting: Invalid face index (int) value type.")
    #     valid = False
    if any(is_invalid_length):
        print("Invalid polyface quantities at index(es): "+[i for i,x in enumerate(is_invalid_length) if x == True])
        print("Aborting: Invalid poly-face index quantity in target shape. Expected GTEQ 3.")
        valid = False
    if not valid:
        __invalid_obj_report( polyfaces, obj_component_type="faces" )

def checkVerticesValidity( vertices ):
    """
    Ensure all vertices (2d list) contain exactly 3 float type values.
    """
    valid = True
    d = np.array(vertices).flat
    try:
        l = [float(x) for x in list(d)]
        is_invalid_type = False
    except ValueError as e:
        is_invalid_type = True
    except TypeError as e:
        is_invalid_type = True
    is_invalid_length = [len(x) != 3 for x in d]
    
    if is_invalid_type:
        print("Aborting: Invalid vertex coordinate value type.")
        valid = False
    if any(is_invalid_length):
        print("Aborting: Invalid vertex coordinate length.")
        valid = False
    if not valid:
        __invalid_obj_report( vertices, obj_component_type="vertices" )


def __invalid_obj_report( polyfaces, obj_component_type ):
    print("Invalid .obj data component is: "+obj_component_type)
    # print(type(polyfaces))
    # print(len(polyfaces))
    # print(type(polyfaces[0]))
    # print(len(polyfaces[0]))
    print("Structure: "+str(array_shape(polyfaces)))
    # raise Exception
    # GracefulShutdown.do_shutdown()