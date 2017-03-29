from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from model_helpers import *
from data_3d import *
  
  
  
  
  
  
# ----------------------------------------------

def make_triangle_face( tri = [( 0.0, 0.0, 0.0), (-1.0,-1.0,-1.0), (1.0,1.0,-1.0)] ):
        draw_triangle_face( tri )
        #draw_normal_line( tri )
        

def draw_triangle_face( tri ):
        glPointSize(1.0)
        glBegin(GL_TRIANGLES)
        glColor3f(1.0,1.0,1.0)
        for t in tri:
                glNormal3f( t[0],t[1],t[2] )
                glVertex3f( t[0],t[1],t[2] )
        glEnd()


def draw_normal_line( tri ):
        c = find_center_of_triangle( tri )
        n = find_perpendicular_of_triangle( tri )
        n = np.add(c, n)
        draw_line( c, n)

def draw_line( start=[0.0, 0.0, 0.0], end=[-2.0,-2.0,-2.0] , thickness=1.0 ):
        s = start
        e = end
        glLineWidth( thickness )
        glBegin(GL_LINES)
        glVertex3f( s[0],s[1],s[2] )
        glVertex3f( e[0],e[1],e[2] )
        glEnd()
        
        
# ----------------------------------------------


def draw_text(text, x, y, DISABLE_LIGHTING=False):
        """ Display 2d text, orthogonally.
        """
        windowWidth     = glutGet(GLUT_WINDOW_WIDTH)
        windowHeight    = glutGet(GLUT_WINDOW_HEIGHT)
        
        # The Projection Matrix
        glMatrixMode(GL_PROJECTION)
        matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glLoadIdentity()
        glOrtho(0.0, windowWidth, 0.0, windowHeight, 0.0, 1.0)
        
        # The Model Matrix
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        glPushMatrix()
        glColor3f(1.0,1.0,1.0)
        glRasterPos2i(x,y)
        if DISABLE_LIGHTING:
                glDisable(GL_LIGHTING)
        
        for c in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))
        glPopMatrix()
        
        
        # Revert the Projection Matrix
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixd(matrix)
        # Set model matrix model
        glMatrixMode (GL_MODELVIEW)
        


def draw_sphere():

    c=M_PI/180.0;            # degrees to radians
    interval = 25.0;
    phiStart = 100.0;        # Default 100
    thetaStart = 180.0;      # Default 180
    
    # ---- for number of 
    phi = -phiStart
    while phi <= (phiStart-interval):
    
        #cout<<"phi "<< phi<<endl;
        phir=c*phi;
        phir20=c*(phi+interval);  # Next phi, that is why phi<=(phiStart-interval)
        
        #glBegin(GL_TRIANGLE_STRIP)
        glBegin(GL_TRIANGLES)
        #glBegin(GL_QUAD_STRIP);
        #glBegin(GL_LINE_STRIP);
        
        theta = -thetaStart
        while theta <= thetaStart:
            thetar=c*theta
            x=sin(thetar)*cos(phir)
            y=cos(thetar)*cos(phir)
            z=sin(phir)
            glVertex3d(x, y, z)
            glNormal3f(x, y, z)
            
            x=sin(phir20)
            x=sin(thetar)*cos(phir20)
            y=cos(thetar)*cos(phir20)
            z=sin(phir20)
            
            glNormal3f(x, y, z)
            glVertex3d(x, y, z)
            
            theta += interval
            
        phi += interval
        glEnd()

def draw_point(point3d=(1,1,1), size=1):
        s = point3d
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor3f(1.0,1.0,1.0)
        glVertex3f( s[0], s[1],s[2])
        glEnd()

def draw_ground():
        glBegin(GL_LINES)
        glColor3f(1.0,1.0,1.0)
        for i in range(16):
            for j in range(16):
                glVertex3f( i,-10,-j) 
                glVertex3f(-i,-10,-j)
                glVertex3f(-i,-10, j)
                glVertex3f( i,-10, j)
        glEnd()
        
def draw_cube():
        # Draw Cube (multiple quads)
        glBegin(GL_QUADS)
 
        glColor3f(0.0,1.0,0.0)
        glVertex3f( 1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f( 1.0, 1.0, 1.0) 
 
        glColor3f(1.0,0.0,0.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f( 1.0,-1.0,-1.0) 
 
        glColor3f(0.0,1.0,0.0)
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
 
        glColor3f(1.0,1.0,0.0)
        glVertex3f( 1.0,-1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0)
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f( 1.0, 1.0,-1.0)
 
        glColor3f(0.0,0.0,1.0)
        glVertex3f(-1.0, 1.0, 1.0) 
        glVertex3f(-1.0, 1.0,-1.0)
        glVertex3f(-1.0,-1.0,-1.0) 
        glVertex3f(-1.0,-1.0, 1.0) 
 
        glColor3f(1.0,0.0,1.0)
        glVertex3f( 1.0, 1.0,-1.0) 
        glVertex3f( 1.0, 1.0, 1.0)
        glVertex3f( 1.0,-1.0, 1.0)
        glVertex3f( 1.0,-1.0,-1.0)

        glEnd()
 

def draw_axes(length=5, width_scale=3):
        l = length
        thickness = 1
        point_size = 1.667
        # z
        glColor3f(0.0,0.0,1.0)
        draw_line((0,0,0), (0,0,l), thickness=thickness)
        for i in range(l+1):
                draw_point((0,0,i), point_size)
        draw_line((0,0,0), (0,0,-l), thickness=thickness)
        for i in range(-l,0,1):
                draw_point((0,0,i), point_size)
                        
        # y     
        glColor3f(0.0,1.0,1.0)
        draw_line((0,0,0), (0,l,0), thickness=thickness)
        for i in range(l+1):
                draw_point((0,i,0), point_size)
        draw_line((0,0,0), (0,-l,0), thickness=thickness)
        for i in range(-l,0,1):
                draw_point((0,i,0), point_size)
        
                
        # x
        glColor3f(1.0,0.0,0.0)
        draw_line((0,0,0), (l,0,0), thickness=thickness)
        for i in range(l+1):
                draw_point((i,0,0), point_size)
        draw_line((0,0,0), (-l,0,0), thickness=thickness)
        for i in range(-l,0,1):
                draw_point((i,0,0), point_size)


def draw_reflection_rays(c, l, r):
    draw_reflection_ray(c, r)
    draw_incident_ray(c, l)
    
def draw_reflection_ray(c, r):
    Origin_Vector = (0,0,0)
    glTranslatef( c[0],c[1],c[2] )
    draw_line(r, Origin_Vector, 5)
    glTranslatef( -c[0],-c[1],-c[2] )

def draw_incident_ray(c, l):
    Origin_Vector = (0,0,0)
    glTranslatef( c[0],c[1],c[2] )
    draw_line(l, Origin_Vector, 1)
    glTranslatef( -c[0],-c[1],-c[2] )

def draw_reflection_to_camera( cameras, tri ):
    for c in cameras:
            face_center = find_center_of_triangle( tri )
            draw_line( c, face_center )             
                    





def draw_cameras( cameraVertices ):
        size = 0.8
        for c in cameraVertices:
            glPushMatrix()
            glTranslatef( c[0],c[1],c[2] )
            glutSolidCube( size )
            glPopMatrix()
        

def draw_wire_sphere( vertex=(0,0,0), size=1, scale=1 ):
        glPushMatrix()
        glTranslatef( vertex[0]*scale, vertex[1]*scale, vertex[2]*scale )
        glutWireSphere(0.4, 9, 9)
        glPopMatrix()


def draw_solid_sphere( vertex=(0,0,0), size=1, scale=1 ):
        glPushMatrix()
        glTranslatef( vertex[0]*scale, vertex[1]*scale, vertex[2]*scale )
        glutSolidSphere(0.4, 9, 9)
        glPopMatrix()                

def draw_dome( scale_multiplier =2,
                show_points     = False,
                show_led_spheres= True,
                show_tris       = False,
                show_lines      = False, 
                get_not_show_tris  = False,
                show_selected_leds = None ):
        """
            Draw the dome into the current OpenGL view using old style opengl. And/Or return its point coordinates.
            -- Ready for refactoring... nasty code resides within -- 
        """
        scale = scale_multiplier
        edges = dome_obj_data.get_dome_edges()
        vertices = dome_obj_data.get_dome_vertices()
        r = [x[1:]  for x in vertices]
        
        #Nastily apply scaling to vertices for return variable.
        r2 = []
        for i in range(len(r)):
            r2.append([])
            for j in range(len(r[i])):
                r2[i].append(  r[i][j]* scale )
        r = r2
        
        glColor3f(1.0,1.0,1.0)
        
        if show_selected_leds != None and type(show_selected_leds) == list:
            # Add the unselected LEDs as points.
            glPointSize(2.0)
            glBegin(GL_POINTS)
            for i in range(len(vertices)):
                    v = vertices[i]
                    if i not in show_selected_leds:
                        glVertex3f( v[1]*scale, v[2]*scale, v[3]*scale )
            glEnd()
            # Add the selected LEDs as spheres.
            size = 0.3
            for i in range(len(vertices)):
                    v = vertices[i]
                    if i in show_selected_leds:
                        glPushMatrix()
                        glTranslatef( v[1]*scale, v[2]*scale, v[3]*scale )
                        glutWireSphere(size, 10, 10)
                        glPopMatrix()
            
        else:
            if show_points:        
                    glPointSize(4.0)
                    glBegin(GL_POINTS)
                    for v in vertices:
                            glVertex3f( v[1]*scale, v[2]*scale, v[3]*scale )
                    glEnd()
            if show_led_spheres:
                    size = 0.1
                    for v in vertices:
                        glPushMatrix()
                        glTranslatef( v[1]*scale, v[2]*scale, v[3]*scale )
                        glutWireSphere(size, 10, 10)
                        glPopMatrix()
            if show_tris and not get_not_show_tris:
                    glPointSize(1.0)
                    glBegin(GL_TRIANGLES)
                    r = []
                    r.append([])
                    c = 0
                    j = 0
                    for e in edges:
                            for i in e[1:]:
                                    c+=1
                                    v = vertices[i-1]
                                    tmpv = [v[1]*scale, v[2]*scale, v[3]*scale]
                                    glVertex3f( tmpv[0], tmpv[1], tmpv[2] )
                                    r[j].append(tmpv)
                                    if c % 3 == 0:
                                            j+=1
                                            r.append([])
                    glEnd()
                    """ Returns a list of lists of lists. The final list has 3 values. The mid-list has 3 vertices.
                        The first list contains all the triangles.
                    """
            if get_not_show_tris:
                    r = []
                    r.append([])
                    c = 0
                    j = 0
                    for e in edges:
                            for i in e[1:]:
                                    c+=1
                                    v = vertices[i-1]
                                    tmpv = [v[1]*scale, v[2]*scale, v[3]*scale]
                                    r[j].append(tmpv)
                                    if c % 3 == 0:
                                            j+=1
                                            r.append([])        
                    r = r[:len(r)-1]    # remove the final empty list.
                    """ Returns a list of lists of lists. The final list has 3 values. The mid-list has 3 vertices.
                        The first list contains all the triangles.
                    """
            if show_lines:
                    glPointSize(1.0)
                    glBegin(GL_LINES)
                    qty_e = 0
                    for e in edges:
                            p1 = vertices[e[1]-1]
                            p2 = vertices[e[2]-1]
                            p3 = vertices[e[3]-1]
                            #edge 1-2
                            glVertex3f( p1[1]*scale, p1[2]*scale, p1[3]*scale )
                            glVertex3f( p2[1]*scale, p2[2]*scale, p2[3]*scale )
                            #edge 2-3
                            glVertex3f( p2[1]*scale, p2[2]*scale, p2[3]*scale )
                            glVertex3f( p3[1]*scale, p3[2]*scale, p3[3]*scale )
                            qty_e += 2
                    glEnd()
        checkShapeValidity( r )
        return r

