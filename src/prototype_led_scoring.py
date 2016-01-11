from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import cos,sin,tan
import numpy as np
import math
import serial
import os, sys
import threading

import draw_calc_lighting
from updateable_line import Updateable_Line
from key_events import key_events

__EXPECTED_VERSION__ = '(2, 7)'
if str(sys.version_info[:2]) != __EXPECTED_VERSION__:
    print "Incorrect Python version, exiting. Check the dependencies and version numbers are correct to execute this module."
    print "Expected "+str(__EXPECTED_VERSION__)
    print "Actual "+str(sys.version_info[:2])
    sys.exit()


#sudo apt-get install python2.7 python-opengl numpy

M_PI = math.pi
ESCAPE = '\033'
SPACE  = ' '
window = 0

#rotation
X_AXIS = 20.0
Y_AXIS = 42.0
Z_AXIS = 0.0
do_rotate = True
viewport_depth = -27.0
default_x, default_z = 0, 0
DIRECTION = 1
lights  = [ (15, 15, 10), (-20.0, -20.0, 20.0), (0.0, -20.0, 0.0), (-20.0, 0.0, 0.0) ]
updateable_line = Updateable_Line(8)
key_events = key_events()











def InitGL(Width, Height): 
 
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) 
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        

        enable_lighting()

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0.3, 0.5, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(.5, .5, .5, .5))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64)

        glShadeModel(GL_SMOOTH)   
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

# Define a simple function to create ctypes arrays of floats:
def vec(*args):
        return (GLfloat * len(args))(*args)
         
        
        
        


def keyPressed(*args):
        global X_AXIS,Y_AXIS,Z_AXIS
        global viewport_depth
        global do_rotate
        global UPD_X, UPD_Y, UPD_Z
        global default_x
        #print args
        rate = 1
        move_viewport   = [GLUT_KEY_UP,GLUT_KEY_DOWN, 'q','e','w','s','a','d']
        update_line     = ['y','h','u','j','i','k']
        
        key_events.key_pressed( args[0] )
        
        s = ""
        if args[0] in [ESCAPE]:
                sys.exit()
        elif args[0] == SPACE:
                do_rotate = not do_rotate   # toggle
        elif args[0] == 'z':
                default_x += rate
        elif args[0] == 'x':
                default_x -= rate
        elif args[0] in move_viewport:
                if args[0] == GLUT_KEY_UP:
                        if viewport_depth <= 0:
                            viewport_depth += rate
                            s = "zoom in"
                elif args[0] == GLUT_KEY_DOWN:
                        viewport_depth -= rate
                        s = "zoom out"
                elif args[0] == 'e':
                        X_AXIS += rate
                        s = "rotate +X"
                elif args[0] == 'q':
                        X_AXIS -= rate
                        s = "rotate -X"
                elif args[0] == 'a':
                        Y_AXIS += rate
                        s = "rotate +Y"
                elif args[0] == 'd':
                        Y_AXIS -= rate
                        s = "rotate -Y"
                elif args[0] == 'w':
                        Z_AXIS += rate
                        s = "rotate +Z"
                elif args[0] == 's':
                        Z_AXIS -= rate
                        s = "rotate -Z"
                print str((X_AXIS, Y_AXIS, Z_AXIS, viewport_depth))+" "+s
        elif args[0] in update_line:        
                x,y,z = updateable_line.get_xyz()
                # uj, ik, ol
                if args[0] == 'u':
                        x -= rate*0.5
                elif args[0] == 'j':
                        x += rate*0.5
                elif args[0] == 'i':
                        y -= rate*0.5
                elif args[0] == 'k':
                        y += rate*0.5
                elif args[0] == 'y':
                        z -= rate*0.5
                elif args[0] == 'h':
                        z += rate*0.5
                print (x,y,z)
                updateable_line.set_xyz(x,y,z)
                
        elif args[0] == GLUT_KEY_RIGHT:
                updateable_line.increment()
        elif args[0] == GLUT_KEY_LEFT:
                updateable_line.decrement()
        

lastMouseX, lastMouseY = 0,0
lastRightMouseX, lastRightMouseY = 0,0
left_dragging = False
right_dragging = False

def drag(x, y):
    global X_AXIS,Y_AXIS
    global left_dragging, lastMouseX, lastMouseY
    global right_dragging, lastRightMouseX, lastRightMouseY
    if left_dragging:
        relativeMoveX = lastMouseX-x
        relativeMoveY = lastMouseY-y
        Y_AXIS -= (relativeMoveX*0.01)
        X_AXIS -= (relativeMoveY*0.01)
    elif right_dragging:
        relativeMoveX = lastRightMouseX-x
        relativeMoveY = lastRightMouseY-y
        x1,y1,z1 = updateable_line.get_xyz()
        newX = x1+relativeMoveX*0.01
        newY = y1-relativeMoveY*0.01
        updateable_line.set_xyz(newX,newY,z1)
    


def mouse(button, state, x, y):
    global X_AXIS,Y_AXIS, viewport_depth
    global left_dragging, lastMouseX, lastMouseY 
    global right_dragging, lastRightMouseX, lastRightMouseY
    left_dragging   = (button == GLUT_LEFT_BUTTON)
    right_dragging  = (button == GLUT_RIGHT_BUTTON)
    wheelUp         = (button == 3)
    wheelDown       = (button == 4)
    if left_dragging:
        lastMouseX = x
        lastMouseY = y
    if right_dragging:
        lastRightMouseX = x
        lastRightMouseY = y
    elif wheelUp:
        if viewport_depth <= 0:
            viewport_depth += 1
    elif wheelDown:
        viewport_depth -= 1
    



def DrawGLScene():
        global X_AXIS,Y_AXIS,Z_AXIS
        global DIRECTION, do_rotate, viewport_depth
        global lights
        global updateable_line
 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        #glMatrixMode (GL_PROJECTION)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(default_x,default_z, viewport_depth)
        glRotatef(X_AXIS,1.0,0.0,0.0)
        glRotatef(Y_AXIS,0.0,1.0,0.0)
        glRotatef(Z_AXIS,0.0,0.0,1.0)
        
        draw_calc_lighting.update_configs_via_keypress(key_events)
        draw_calc_lighting.draw( updateable_line )
        
        
        if do_rotate:
                #X_AXIS = X_AXIS - 0.05
                Y_AXIS = Y_AXIS - 1.0
                #Z_AXIS = Z_AXIS - 0.05
 
        glutSwapBuffers()


def enable_lighting():
        global lights           
        #print "Max number of OpenGL lights: ... it is 8... although it reports: "+str(GL_MAX_LIGHTS)
        glEnable(GL_LIGHTING)
        li_num = 16384  # GL_LIGHT0, max of 8
        for l in lights:
                glEnable(li_num)
                glLight(li_num, GL_POSITION, vec(l[0],l[1],l[2], 1))    # http://pyopengl.sourceforge.net/documentation/manual-3.0/glLight.html
                glLight(li_num, GL_SPECULAR, vec(.5, .5, 1, 1))
                glLight(li_num, GL_DIFFUSE,  vec(1, 1, 1, 1))
                li_num += 1
                if li_num > 16391:
                        print "MAX NUM OF LIGHTS EXCEEDED. Truncating num of lights at 8."
                        break
        






 
def main():
        global window 
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(800,600)
        glutInitWindowPosition(0,5)
        glViewport(0, 0, 500, 500);
        window = glutCreateWindow('LightStage V3 - Target Illumination Score Tool')
 
        glutDisplayFunc(DrawGLScene)
        glutIdleFunc(DrawGLScene)
        glutKeyboardFunc(keyPressed)
        glutSpecialFunc(keyPressed)
        glutMouseFunc(mouse)
        glutMotionFunc(drag)
        InitGL(640, 480)
        glutMainLoop()
 
if __name__ == "__main__":
        main() 
