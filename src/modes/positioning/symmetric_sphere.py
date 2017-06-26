from __future__ import division
import math
from math import sin,cos

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Visualise_with_PyGame:
    def __init__(self):
        pass

    def shape(self, vertices):
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for vertex in vertices:
            glVertex3fv(vertex)
        glEnd()

    def display( self, vertices ):
        pygame.init()
        display = (800, 600)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

        glTranslatef(0.0, 0.0, -5)

        while True:
            for event in pygame.event.get():
                if event.type in [pygame.QUIT]:
                    pygame.quit()
                    quit()

            glRotatef(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.shape(vertices)
            pygame.display.flip()
            pygame.time.wait(10)


def get_45point_circular_symmetry_sphere( num_of_longditudinal_intervals=5 ):
    """
    A sphere with circular symmetry at five z-coordinates: poles (90/-90), tropics (45/-45) and equator (0).
    Adapted from Leonsim's code here: https://github.com/leonsim/sphere/blob/9ec92d2f5411171776e1176be58468af68a93442/Sphere.cpp
    """
    vertices = []
    c = math.pi / 180.0  # Degrees to radians
    interval = 180/ num_of_longditudinal_intervals  # Default 30
    phiStart = 90.0  # Default 100
    thetaStart = 180.0  # Default 180

    phi = -phiStart
    while phi <= (phiStart):
        phir = c * phi
        theta = -thetaStart
        while theta <= thetaStart:
            thetar = c * theta
            x = sin(thetar) * cos(phir)
            y = cos(thetar) * cos(phir)
            z = sin(phir)
            v1 = (x, y, z)
            vertices.append(v1)
            theta += interval
        phi += interval
    return vertices


def get_45point_spiralling_sphere( num_of_spirals = 4, num_of_vertices = 45):
    """
    A sphere of spiralling points. Each point is equally spaced on the x,y,z axes. The equal spacing is calculated by dividing the straight-line spiral distance by 45.
    Adapted from Leonsim's code here: https://github.com/leonsim/sphere/blob/9ec92d2f5411171776e1176be58468af68a93442/Sphere.cpp
    """
    vertices = []
    xy_degree_change = (num_of_spirals * 360) / num_of_vertices
    z_degree_change = 360 / num_of_vertices

    c = math.pi / 180.0  # Degrees to radians
    phiStart = 90.0  # Default 100
    thetaStart = 180.0  # Default 180
    theta = -thetaStart
    phi = -phiStart
    while phi <= (phiStart):
        phir = c * phi

        thetar = c * theta
        x = sin(thetar) * cos(phir)
        y = cos(thetar) * cos(phir)

        z = sin(phir)

        v1 = (x, y, z)
        vertices.append(v1)
        theta += xy_degree_change
        phi += z_degree_change
    return vertices


def get_45point_spiralling_sphere_with_normal_zaxis_dist( num_of_spirals = 4, num_of_vertices = 45):
    """
    A sphere of spiralling points. Each point is equally spaced on the x,y,z axes. The equal spacing is calculated by dividing the straight-line spiral distance by 45.
    Adapted from Leonsim's code here: https://github.com/leonsim/sphere/blob/9ec92d2f5411171776e1176be58468af68a93442/Sphere.cpp
    """
    vertices = []
    xy_degree_change = (num_of_spirals * 360) / num_of_vertices
    zaxis_dist = get_normalised_normal_curve()

    c = math.pi / 180.0  # Degrees to radians
    phiStart = 90.0  # Default 100
    thetaStart = 180.0  # Default 180
    theta = -thetaStart
    phi = -phiStart
    index = -1
    while phi <= (phiStart):
        index +=1
        phir = c * phi

        thetar = c * theta
        x = sin(thetar) * cos(phir)
        y = cos(thetar) * cos(phir)

        z = sin(phir)

        v1 = (x, y, z)
        vertices.append(v1)
        theta += xy_degree_change
        print("Vertex:"+str(index)+", zAxis:"+str(len(zaxis_dist))+", Vertices:"+str(len(vertices)))

        z_degree_change = (360 /num_of_vertices) * zaxis_dist[index]
        phi += z_degree_change
    return vertices


def get_normal_curve_y_value(x=1, mean=22.5, sigma=2):
    e_pow = math.pow(math.e, -(((x - mean) ** 2) / ((2 * sigma) ** 2)))
    y = 1 / (sigma * math.sqrt(2 * math.pi)) * e_pow
    return y


def get_normalised_normal_curve( invert=True, mean=22.5, sigma=7 , qty_of_values=45):
    l = []
    for i in range(0, qty_of_values):
        if invert:
            y = -get_normal_curve_y_value(x=i, mean=mean, sigma=sigma)
        else:
            y = get_normal_curve_y_value(x=i, mean=mean, sigma=sigma)
        l.append(y)
    n = normalise(l)
    return n


def normalise(l):
    min_y = min(l)
    max_y = max(l)
    normalised = []
    for x in l:
        normalised.append((x - min_y) / (max_y - min_y))
    return normalised


def get_sphere():
    # return get_45point_circular_symmetry_sphere( num_of_longditudinal_intervals=5 )
    # return get_45point_spiralling_sphere( num_of_spirals = 6, num_of_vertices = 45 )
    return get_45point_spiralling_sphere_with_normal_zaxis_dist( num_of_spirals = 6, num_of_vertices = 45 )
    # return get_45point_circular_symmetry_sphere( num_of_longditudinal_intervals=6 )

def test_curve():
    n = get_normalised_normal_curve()
    import matplotlib.pyplot as plt
    plt.plot(n)
    # plt.savefig("normal_y.pdf")
    plt.show()

if __name__ == "__main__":
    test_curve()
    # vertices = get_sphere()
    # x = Visualise_with_PyGame()
    # x.display( vertices )