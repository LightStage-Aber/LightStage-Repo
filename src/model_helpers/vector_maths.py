from __future__ import division
import numpy as np
import math
import sys



def get_reflectance_ray(l , n, a=[0,1,0]):
        d = (-l[0],-l[1],-l[2])  
#        if False:
#                r = (-d[0],d[1],-d[2])  
#        elif False:
#                """http://math.stackexchange.com/a/13266/197674 - Solution by Phrogz
#                        r = d -2(d.n)n
#                """
#                d = np.array(d)
#                mult = np.multiply( np.dot(d,n) , 2)
#                subr = np.multiply( mult, n)
#                r = np.subtract( d , subr )
#        else:
        """ source: http://math.stackexchange.com/a/13266/197674 - Solution 2 by Zarrax
                r = d-((2d.n)/(|n|^2))n
        """
        #r = np.subtract(d  , np.multiply( np.multiply(np.dot( d, n),2) , n ) )
        d = np.array(d)
        n = np.array(n)
        nmag = np.linalg.norm(n)
        numerator = np.dot( np.multiply(d,2) , n)
        denominator = math.pow(nmag,2)
        divis = np.divide(numerator, denominator)
        #bodmas
        subr = np.multiply( divis, n )
        r = np.subtract(d , subr)
                
        return r


def get_incidence_angle( tri, orgin ):
        surface_normal = find_perpendicular_of_triangle( tri )  #(tri[2],tri[1],tri[0])
        n1 = normalize( surface_normal )
        n2 = normalize( orgin )
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        return radians, degrees


def find_center_of_triangle( tri ):        
        t = np.array(tri)
        t0 = t[0]
        t1 = t[1]
        t2 = t[2]
        x = (t0[0] + t1[0] + t2[0]) /3
        y = (t0[1] + t1[1] + t2[1]) /3
        z = (t0[2] + t1[2] + t2[2]) /3
        return (x,y,z)

def get_angle_between_two_lines_3points( c, p1, p2):
        """ Angle between two lines that have a shared point <var> 'c'
        """
        l1 = find_perpendicular_of_line( c, p1 )
        l2 = find_perpendicular_of_line( c, p2 )
        n1 = normalize( l1 )
        n2 = normalize( l2 )
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        return radians, degrees
        
def get_angle_between_two_lines( l1, l2 ):
        l1 = find_perpendicular_of_line( l1[0],l1[1] )
        l2 = find_perpendicular_of_line( l2[0],l2[1] )
        n1 = normalize( l1 )
        n2 = normalize( l2 )
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        return radians, degrees


def get_angle_between_two_points( l1, l2 ):
        """ Angle between two points that have the shared point of origin.
        """
        n1 = normalize( l1 )
        n2 = normalize( l2 )
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        return radians, degrees

def get_angle_between_two_planes( tri, originTri ):
        surface_normal = find_perpendicular_of_triangle( tri )
        surface_normal2 = find_perpendicular_of_triangle( originTri )
        n1 = normalize( surface_normal )
        n2 = normalize( surface_normal2 )
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        return radians, degrees

def find_perpendicular_of_line( p1,p2 ):
        a = np.cross(p1, p2)
        norm = normalize(a)
        return norm

def find_perpendicular_of_triangle( tri ):
        v1 = np.subtract(tri[1], tri[0])
        v2 = np.subtract(tri[2], tri[0])
        a = np.cross(v1, v2)
        if len(a) != 3:
                print "Degenerate_triangle_error"
                sys.exit(-1)
        norm = normalize(a)
        return norm

def rotate_triangles( triangles, axis, degrees ):
    for i in range(len(triangles)):
        triangles[i] = rotate_tri( triangles[i] , axis, degrees )
    return triangles
    
def rotate_tri( tri , axis, degrees ):
    for i in range(len(tri)):
        tri[i] = rotate_vector( tri[i], axis, degrees )
    return tri

def rotate_vector( vector, axis, degrees ):
    """ Rotate a vector, on the axis, a given number of degrees. Return the new vector.
        Usage:  new_vec = rotate_vector( (1,2,3), (0,1,0), 90 ) # rotate 90 degrees on y-axis
    """
    theta = math.radians(degrees)
    return np.dot(__rotation_matrix(axis, theta), vector)
    #v = [0, 0, 9.5]
    #axis = [0, 1, 0]
    # [ 2.74911638  4.77180932  1.91629719]


def __rotation_matrix(axis, theta):
    """ --- SOURCE: http://stackoverflow.com/a/6802723
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    
    Example:
        v = [3, 5, 0]
        axis = [4, 4, 1]
        theta = 1.2 
        print(np.dot(rotation_matrix(axis,theta), v)) 
        # [ 2.74911638  4.77180932  1.91629719]
    """
    axis = np.asarray(axis)
    theta = np.asarray(theta)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2)
    b, c, d = -axis*math.sin(theta/2)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])




def plane_rotation( n1, n2 ):
        axis, degrees = [0,0,0],0
        normals_not_same = len(set(n1).intersection(n2)) != len(n1)
        if normals_not_same:
                axis, degrees = angle_between_two_vectors( n1, n2 )     # Get angle difference between of current and new tri plane using perpendicular of each plane.
        return axis, degrees






def normalize(a):
    a = np.array(a)
    return np.divide(a, math.sqrt(np.dot(a, a))) 
    #   return np.divide(a, np.linalg.norm(a)) -- is slower according to timeit test
    #    In [7]: np.divide(a, math.sqrt(np.dot(a, a)))
    #    Out[7]: array([ 0.42426407,  0.56568542,  0.70710678])
    #    In [8]: np.divide(a, np.linalg.norm(a))
    #    Out[8]: array([ 0.42426407,  0.56568542,  0.70710678])
    #    In [9]: %timeit np.divide(a, np.linalg.norm(a))
    #    100000 loops, best of 3: 15.8 us per loop
    #    In [10]: %timeit np.divide(a, math.sqrt(np.dot(a, a)))
    #    100000 loops, best of 3: 10.2 us per loop


#def normalize(v):
#    """Source: http://stackoverflow.com/questions/24705225/opengl-rotation-from-velocity-vector
#    """
#    v = np.array(v)
#    norm = np.linalg.norm(v)
#    if norm > 1.0e-8:  # arbitrarily small
#        v = v/norm
#    else:
#        return v

def angle_between_two_vectors( n1, n2 ):
        radians = math.acos( np.dot( n1, n2 ) )
        degrees = math.degrees( radians )
        axis = np.cross(n1, n2)
        return axis, degrees

