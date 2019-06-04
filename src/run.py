from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import scipy, numpy
import sys


__EXPECTED_VERSION__ = '(2, 7)'
if str(sys.version_info[:2]) != __EXPECTED_VERSION__:
    print("Unexpected Python version, attempting to continue. Check the dependencies and version numbers are compatible to execute this module.")
    print("Expected "+str(__EXPECTED_VERSION__))
    print("Actual "+str(sys.version_info[:2]))

EXPECTED_VERSION_OPENGL = ['3.1.1b1','3.1.1a1','3.0.2', '3.1.0']
if str(OpenGL.__version__) not in EXPECTED_VERSION_OPENGL:
    print("Unexpected OpenGL version, attempting to continue. Check the dependencies and version numbers are compatible to execute this module.")
    print("Expected "+str(EXPECTED_VERSION_OPENGL))
    print("Actual "+str(OpenGL.__version__))

EXPECTED_VERSION_SCIPY = ['0.18.1','0.19.0','1.2.1']
if str(scipy.__version__) not in EXPECTED_VERSION_SCIPY:
    print("Unexpected scipy version, attempting to continue. Check the dependencies and version numbers are compatible to execute this module.")
    print("Expected "+str(EXPECTED_VERSION_SCIPY))
    print("Actual "+str(scipy.__version__))

EXPECTED_VERSION_NUMPY = ['1.11.2','1.12.1','1.16.3']
if str(numpy.__version__) not in EXPECTED_VERSION_NUMPY:
    print("Unexpected numpy version, attempting to continue. Check the dependencies and version numbers are compatible to execute this module.")
    print("Expected "+str(EXPECTED_VERSION_NUMPY))
    print("Actual "+str(numpy.__version__))

import tool_managers
from model_helpers import Updateable_Line
from options import Key_Events, get_parsed_commandline_options


class _StateData(object):
        X_AXIS = 20.0
        Y_AXIS = 42.0
        Z_AXIS = 0.0
        do_rotate = True
        viewport_depth = -27.0
        default_x = 0
        default_z = 0
        @staticmethod
        def toggle_rotate():
            _StateData.do_rotate = not _StateData.do_rotate  # toggle


class OpenGLInputHandler:

    def __init__(self):
        self.updateable_line = Updateable_Line(8)
        self.keyEvents = Key_Events()

        self.lastMouseX, self.lastMouseY = 0, 0
        self.lastRightMouseX, self.lastRightMouseY = 0, 0
        self.left_dragging = False
        self.right_dragging = False

    def keyPressed(self, *args):
        ESCAPE = '\033'
        SPACE = ' '
        rate = 1
        move_viewport = [GLUT_KEY_UP, GLUT_KEY_DOWN, 'q', 'e', 'w', 's', 'a', 'd']
        update_line = ['y', 'h', 'u', 'j', 'i', 'k']

        self.keyEvents.key_pressed(args[0])

        s = ""
        if args[0] in [ESCAPE]:
            sys.exit(0)
        elif args[0] == SPACE:
            _StateData.toggle_rotate()
        elif args[0] == 'z':
            _StateData.default_x += rate
        elif args[0] == 'x':
            _StateData.default_x -= rate
        elif args[0] in move_viewport:
            if args[0] == GLUT_KEY_UP:
                if _StateData.viewport_depth <= 0:
                    _StateData.viewport_depth += rate
                    s = "zoom in"
            elif args[0] == GLUT_KEY_DOWN:
                _StateData.viewport_depth -= rate
                s = "zoom out"
            elif args[0] == 'e':
                _StateData.X_AXIS += rate
                s = "rotate +X"
            elif args[0] == 'q':
                _StateData.X_AXIS -= rate
                s = "rotate -X"
            elif args[0] == 'a':
                _StateData.Y_AXIS += rate
                s = "rotate +Y"
            elif args[0] == 'd':
                _StateData.Y_AXIS -= rate
                s = "rotate -Y"
            elif args[0] == 'w':
                _StateData.Z_AXIS += rate
                s = "rotate +Z"
            elif args[0] == 's':
                _StateData.Z_AXIS -= rate
                s = "rotate -Z"
            print(str((_StateData.X_AXIS, _StateData.Y_AXIS, _StateData.Z_AXIS,
                       _StateData.viewport_depth)) + " " + s)
        elif args[0] in update_line:
            x, y, z = self.updateable_line.get_xyz()
            # uj, ik, ol
            if args[0] == 'u':
                x -= rate * 0.5
            elif args[0] == 'j':
                x += rate * 0.5
            elif args[0] == 'i':
                y -= rate * 0.5
            elif args[0] == 'k':
                y += rate * 0.5
            elif args[0] == 'y':
                z -= rate * 0.5
            elif args[0] == 'h':
                z += rate * 0.5
            print(x, y, z)
            self.updateable_line.set_xyz(x, y, z)

        elif args[0] == GLUT_KEY_RIGHT:
            self.updateable_line.increment()
        elif args[0] == GLUT_KEY_LEFT:
            self.updateable_line.decrement()

    def drag(self, x, y):

        # On left click drag, move the viewport..
        if self.left_dragging:
            relativeMoveX = self.lastMouseX-x
            relativeMoveY = self.lastMouseY-y
            _StateData.Y_AXIS -= (relativeMoveX*0.01)
            _StateData.X_AXIS -= (relativeMoveY*0.01)

        # On right click drag, move the updateable line slowly along the X/Y axis.
        elif self.right_dragging:
            relativeMoveX = self.lastRightMouseX-x
            relativeMoveY = self.lastRightMouseY-y
            x1,y1,z1 = self.updateable_line.get_xyz()
            newX = x1+relativeMoveX*0.01
            newY = y1-relativeMoveY*0.01
            self.updateable_line.set_xyz(newX, newY, z1)

    def mouse(self, button, state, x, y):

        self.left_dragging  = (button == GLUT_LEFT_BUTTON)
        self.right_dragging = (button == GLUT_RIGHT_BUTTON)
        wheelUp             = (button == 3)
        wheelDown           = (button == 4)

        if self.left_dragging:
            self.lastMouseX = x
            self.lastMouseY = y
        if self.right_dragging:
            self.lastRightMouseX = x
            self.lastRightMouseY = y
        elif wheelUp:
            if _StateData.viewport_depth <= 0:
                _StateData.viewport_depth += 1
        elif wheelDown:
            _StateData.viewport_depth -= 1


class OpenGLRunner(object):
    __window = 0
    # __lights = [(15, 15, 10), (-20.0, -20.0, 20.0), (0.0, -20.0, 0.0), (-20.0, 0.0, 0.0)]
    __lights = [(10, 0, 0), (0, 10, 0), (0, 0, 10), 
                (20, 0, 0), (0, 20, 0), (0, 0, 20), 
                #(-20.0, 0, 0), (0.0, -20.0, 0.0), (0, 0.0, -20.0)
                ]

    def __init__(self, input_handler, draw_callback_func):
        self.__keyPressed_func  = input_handler.keyPressed
        self.__mouse_func       = input_handler.mouse
        self.__drag_func        = input_handler.drag
        self.__draw_callback_func = draw_callback_func

    def InitGL(self, Width, Height):
        global GL_LESS, GL_DEPTH_TEST, GL_CULL_FACE, GL_FRONT_AND_BACK, \
            GL_AMBIENT_AND_DIFFUSE, GL_SHININESS, GL_PROJECTION, GL_MODELVIEW, GL_SMOOTH

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST),
        glEnable(GL_CULL_FACE)

        self.enable_lighting()

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.__vec(0.2, 0.2, 0.2, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.__vec(1, 1, 1, .2))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 99)
        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(Width) / float(Height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)


    def DrawGLScene(self):
            global GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glTranslatef(_StateData.default_x, _StateData.default_z, _StateData.viewport_depth)
            glRotatef(_StateData.X_AXIS,1.0,0.0,0.0)
            glRotatef(_StateData.Y_AXIS,0.0,1.0,0.0)
            glRotatef(_StateData.Z_AXIS,0.0,0.0,1.0)

            self.__draw_callback_func()

            if _StateData.do_rotate:
                    #_StateData.X_AXIS = _StateData.X_AXIS - 0.05
                    _StateData.Y_AXIS = _StateData.Y_AXIS - 1.0
                    #_StateData.Z_AXIS = _StateData.Z_AXIS - 0.05

            glutSwapBuffers()


    def enable_lighting(self):
            global GL_LIGHTING, GL_POSITION, GL_SPECULAR, GL_DIFFUSE, GL_AMBIENT
            glEnable(GL_LIGHTING)
            li_num = 16384  # GL_LIGHT0, max of 8
            for l in OpenGLRunner.__lights:
                    glEnable(li_num)
                    glLight(li_num, GL_POSITION, self.__vec(l[0], l[1], l[2], 1))    # http://pyopengl.sourceforge.net/documentation/manual-3.0/glLight.html
                    glLight(li_num, GL_AMBIENT, self.__vec(.5, .5, 5, 1))
                    glLight(li_num, GL_DIFFUSE, self.__vec(.5, .5, .5, 1))
                    glLight(li_num, GL_SPECULAR, self.__vec(1, 1, 1, 1))
                    li_num += 1
                    if li_num > 16391:
                            print("MAX NUM OF LIGHTS EXCEEDED. Truncating num of lights at 8.")
                            break
    
    def select_menu(self, choice):
        def _toggle_rotate():
            _StateData.toggle_rotate()
        def _exit():
            sys.exit(0)
        {
            1: _toggle_rotate,
            2: _exit
        }[choice]()
        glutPostRedisplay()
        return 0

    def right_click_menu(self):
        from ctypes import c_int,c_void_p
        import platform
        #platform specific imports:
        if (platform.system() == 'Windows'):
            #Windows
            from ctypes import WINFUNCTYPE
            CMPFUNCRAW = WINFUNCTYPE(c_int, c_int)
        else:
            #Linux
            from ctypes import CFUNCTYPE
            CMPFUNCRAW = CFUNCTYPE(c_int, c_int)
            
        myfunc = CMPFUNCRAW(self.select_menu)

        color_submenu = glutCreateMenu( myfunc )
        glutAddMenuEntry("Toggle Rotation", 1);
        glutAddMenuEntry("Quit", 2);
        glutAttachMenu(GLUT_RIGHT_BUTTON);

    def draw(self):
            glutInit()
            glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
            glutInitWindowSize(800,600)
            glutInitWindowPosition(0,5)
            OpenGLRunner.__window = glutCreateWindow(b'LightStage - Target Illumination Score Tool')
            glViewport(0, 0, 500, 500);

            self.right_click_menu()

            glutDisplayFunc(self.DrawGLScene)
            glutIdleFunc(self.DrawGLScene)
            glutKeyboardFunc(self.__keyPressed_func)
            glutSpecialFunc(self.__keyPressed_func)
            glutMouseFunc(self.__mouse_func)
            glutMotionFunc(self.__drag_func)
            self.InitGL(640, 480)
            glutMainLoop()


    # Define a simple function to create ctypes arrays of floats:
    @staticmethod
    def __vec(*args):
        return (GLfloat * len(args))(*args)


class LightStageApp(object):

    def __init__(self):
        tool_managers.define_help()
        self.__input_handler = OpenGLInputHandler()
        self.__keyEvents = self.__input_handler.keyEvents
        self.__updateable_line = self.__input_handler.updateable_line
        self.__tool = tool_managers.Tool()

    def main(self):
        PARSE_OPTIONS,PARSE_ARGS = get_parsed_commandline_options()
        do_demo                 = PARSE_OPTIONS.EVALUATION == 1
        do_evaluation_or_tuning = PARSE_OPTIONS.EVALUATION == 2 or PARSE_OPTIONS.EVALUATION == 3

        if do_demo:
            run = OpenGLRunner(self.__input_handler, self.__draw_callback)
            run.draw()
        elif do_evaluation_or_tuning:
            self.__tool.run(self.__updateable_line)
        else:
            pass

    def __draw_callback(self):

        # todo: This is a hack. Rework tool_managers.py to encapsulate keypress (and other) globals into a Config class, then this call should affect that object state.
        tool_managers.update_configs_via_keypress(self.__keyEvents)
        self.__tool.run( self.__updateable_line )

if __name__ == "__main__":
        x = LightStageApp()
        x.main()
