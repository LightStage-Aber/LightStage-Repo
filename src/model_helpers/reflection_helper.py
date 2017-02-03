from __future__ import division
import numpy as np
import math
import sys
from vector_maths import *
from OpenGL.GL import *


def is_front_facing_reflection(tri, l, r ):
    rad,d   = get_incidence_angle( tri, l )
    incident_deg = d
    rad,d   = get_incidence_angle( tri, r )
    reflection_deg = d    

    if round(incident_deg, 4) != round(reflection_deg, 4):
        print "incident "+str(round(incident_deg, 4))+" and reflection "+str(round(reflection_deg, 4))+" angles, from surface normal, not equal."
        raise ValueError
    
    total_angle = incident_deg+reflection_deg
    is_front_facing  = (total_angle > 0.0 and total_angle < 180.0)
    
    return is_front_facing

def is_front_facing_reflection_to_camera(tri, cameraPos):
    print_debug = False
    rad,d   = get_incidence_angle( tri, cameraPos )
    surface_to_camera_reflection_deg = d
    angle   = surface_to_camera_reflection_deg
    is_front_facing  = (angle > -90.0 and angle < 90.0)
    
    if print_debug:
        print ("Surface to Camera Reflection Angle: ",surface_to_camera_reflection_deg)
        print ("Is Front Facing: ",is_front_facing)
    
    return is_front_facing

def get_angle_from_reflection_to_camera(c, r, view):
    Origin_Vector = (0,0,0)
    print_debug = False
    glTranslate( c[0],c[1],c[2] )
    if print_debug: draw_triangle_face( [Origin_Vector, r, view] )
    rad,d = get_angle_between_two_points(r, view )
    glTranslate( -c[0],-c[1],-c[2] )
    angle = d
    is_valid_reflection_angle   = angle >= 0.0 and angle <= 180.0
    
    if print_debug: print ("Point Angle: ",rad,d)
    if not is_valid_reflection_angle:
        raise ValueError("Aborting due to invalid reflection angle to camera.\nExpected: 0-180 degrees\nAcutal: "+str(angle)+" degrees")
    return rad,d


def __debug_is_cullable_reflection(tri, OTri, l, r, c ):
    """ Debug function to gain further information on reflection ray angles.
    """
    print_debug = True
    rad,d   = get_incidence_angle( tri, l )
    incident_deg = d
    rad,d   = get_incidence_angle( tri, r )
    reflection_deg = d    
    
    total_angle = incident_deg+reflection_deg
    is_front_facing  = (total_angle > 0.0 and total_angle < 180.0)
    
    if print_debug:
        if print_debug: print ("Incident Angle: ",incident_deg)
        if print_debug: print ("Reflection Angle: ",reflection_deg)
        if print_debug: print ("Reflection+Incident Angle: ",total_angle)
        rad,d = get_angle_between_two_planes(tri, OTri )
        if print_debug: print ("Plane Angle: ",rad,d)
        rad,d = get_angle_between_two_points(l, r)
        if print_debug: print ("Point Angle: ",rad,d)
        rad,d = get_angle_between_two_lines([l,c], [r,c])
        if print_debug: print ("Line Angle: ",rad,d)
        if print_debug: print ("Is Front Facing: ",is_front_facing)
    
    return is_front_facing



def reflect_no_rotate( c, l, normal ):
        glTranslatef( c[0],c[1],c[2] )
        l  = np.subtract(l, c)
        r  = get_reflectance_ray(l, normal)
        glTranslatef( -c[0],-c[1],-c[2] )
        return l, r


