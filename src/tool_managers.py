from __future__ import division


from options import get_parsed_commandline_options
from data_3d import WaveFront
# from data_3d import *
from modes import *
from file_utils import *
from modes.manipulate_results_data import *
import logging
from service import GracefulShutdown



# ======================================================================
# --- Parameterised config update
# ======================================================================
PARSE_OPTIONS,PARSE_ARGS = get_parsed_commandline_options()


class App:
    #@todo: Refactor the globals in this module into the 'App' class in 'config.py'.
    pass






# Program's Config
SELECT_BEST_LEDS             = True if PARSE_OPTIONS.EVALUATION == 1 else False
#TODO:-- Bug due to mutable state reused for multiple purposes (toggle_test_evaluation_mode() function), replacing with PARSE_OPTIONS.EVALUATION == 1.
#     -- Solution: Repurpose this module as DEMO MODE ONLY. Move all evaluations to another model and module. Move argument parsing to the MAIN.

QTY_OF_BEST_LEDS_REQUIRED    = PARSE_OPTIONS.LEDS_QTY
default_QTY_OF_BEST_LEDS_REQUIRED = lambda: PARSE_OPTIONS.LEDS_QTY
TARGET_SHAPE                 = PARSE_OPTIONS.TARGET_SHAPE          # None
TARGET_SCALE                 = PARSE_OPTIONS.TARGET_SCALE          # 0.01
TARGET_TRANSLATION           = eval(PARSE_OPTIONS.TARGET_TRANSLATION)    # (0,-3,0)

# Display Configuration for Scoring
USE_SHADING_SCORE       = True if PARSE_OPTIONS.DISPLAY_EVALUATION_METRIC_OPTION == 1 else False
USE_COVERAGE_SCORE      = not USE_SHADING_SCORE
SCORE_DESCRIPTION       = "Intensity Score" if USE_SHADING_SCORE else "Coverage Error"
CSV_METRIC_COLUMN_INDEX = 1 if USE_SHADING_SCORE else 3







# Extra Detailed Program Configs:
DO_EVALUATIONS      = True
DRAW_REFLECTION_RAY = True
DRAW_INCIDENT_RAY   = True
DRAW_CAMERA_REFLECTION_RAY  = True
scale = property_to_number(section="FrameModel", key="frame.scale", vmin=1, vmax=20, vtype=float)
scale = scale if scale is not None else 8
TARGET_ROTATIONS = 6
TARGET_ROTATION_AXIS = (0,1,0)
TARGET_ROTATION_DEGREES=(360/TARGET_ROTATIONS)


# Camera Configuration:
camera_layout = CameraLayout_RealisticBias( scale ) if PARSE_OPTIONS.CAMERA_LAYOUT == 1 else CameraLayout_EvenBias( scale ) #cameraVertices = camera_layout.getCameraPositions() # cameraPos = camera_layout.getDefaultCameraPos()
#CAMERA_POSITION_DESCRIPTION = camera_layout.getDescription()
CAMERA_SHORT_DESCRIPTION    = camera_layout.getShortDescription()






LED_SCORE_LOG_FILE   = PARSE_OPTIONS.LED_SCORE_LOG_FILE if PARSE_OPTIONS.LED_SCORE_LOG_FILE != None and os.path.exists(PARSE_OPTIONS.LED_SCORE_LOG_FILE) else ""
logged_score_to_file = False
BEST_LEDS            = None
TARGET_TRIANGLES     = None
TARGET_SHAPE_NAME    = ''
BEST_LED_DATA_HEADER = None
BEST_LED_DATA        = None
#BEST_LED_DATA_HEADER = file_io.read_in_csv_file_header_to_list(LED_SCORE_LOG_FILE)  if SELECT_BEST_LEDS else None
#BEST_LED_DATA        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=True)  if SELECT_BEST_LEDS else None


HELP = {}


# ======================================================================
# --- Live config update
# ======================================================================

def define_help():
    global HELP
    HELP['r'] = "Toggle scoring (maximised intensity / maximised target coverage)."
    HELP['c'] = "Toggle camera positioning."
    HELP['t'] = "Toggle test evaluation mode to verify angles and scoring.\n\t- Use Left-Arrow and Right-Arrow to change LED.\n\t- Use y/h/u/j/i/k to update incident ray X,Y,Z coordinate."
    #HELP['n'] = "Toggle target normals"
    HELP['l'] = "Load new score file."
    HELP['+'] = "Increase LEDs selected. (Shading Score only. Unchecked bounds.)"
    HELP['-'] = "Decrease LEDsdata_3d selected. (Shading Score only. Unchecked bounds.)"
    HELP['ws,ad,qe'] = "Manipulate the viewport XYZ positions (ws, ad, qe), or click-drag with mouse."
    HELP['Up']    = "Zoom in / Wheel-up"
    HELP['Down']  = "Zoom out / Wheel-down"
    HELP['F1']    = "Display help."
    HELP['Space'] = "Toggle scene rotation."
    HELP['Esc']   = "Exit."
    print("\nPress F1 to display help.\n")

def update_configs_via_keypress(key_events):
    k = key_events.get_key()
    if k == '':
        return
    if k == 'r':
        toggle_reflection_score()
    elif k == 'c':
        toggle_camera_setup()
    elif k == 't':
        toggle_test_evaluation_mode()
    elif k == 'l':
        load_new_score_file()
    elif k == GLUT_KEY_F1:
        toggle_help()
    elif k == '+':
        increment_LED_quantity()
    elif k == '-':
        decrement_LED_quantity()
        

def toggle_help():
    global HELP
    print("---Help:---")
    for k in HELP:
        print("  "+str(k) +"\t"+ str(HELP[k]))
    print("-----------")
    
def toggle_reflection_score():
    global USE_SHADING_SCORE, USE_COVERAGE_SCORE, SCORE_DESCRIPTION, CSV_METRIC_COLUMN_INDEX, BEST_LEDS, QTY_OF_BEST_LEDS_REQUIRED
    USE_SHADING_SCORE       = not USE_SHADING_SCORE     # T -> F
    USE_COVERAGE_SCORE      = not USE_SHADING_SCORE     # F -> not F -> T
    SCORE_DESCRIPTION       = "Shading Score" if USE_SHADING_SCORE else "Coverage Error"
    CSV_METRIC_COLUMN_INDEX = 1 if USE_SHADING_SCORE else 3
    BEST_LEDS               = None
    if USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED = default_QTY_OF_BEST_LEDS_REQUIRED()
    msg = "Toggled scoring to Shading Score" if USE_SHADING_SCORE else "Toggled scoring to Coverage Score"
    print(msg)


def toggle_camera_setup():
    global scale, camera_layout
    camera_layout = CameraLayout_EvenBias( scale ) if type(camera_layout) == CameraLayout_RealisticBias else CameraLayout_RealisticBias( scale )    
    msg = "Toggled camera to "+camera_layout.getShortDescription()
    print(msg)


def toggle_test_evaluation_mode():
    global SELECT_BEST_LEDS, DO_EVALUATIONS
    SELECT_BEST_LEDS = not SELECT_BEST_LEDS
    DO_EVALUATIONS = False if not SELECT_BEST_LEDS else True
    msg = "Toggled test evaluation mode off" if SELECT_BEST_LEDS else "Toggled test evaluation mode on."
    print(msg)
    
def load_new_score_file():
    global LED_SCORE_LOG_FILE, BEST_LED_DATA, BEST_LED_DATA_HEADER, BEST_LEDS
    print(" === LOAD NEW SCORE FILE ===")
    print("Enter new input score filename and press enter:")
    print(" --- Current filename: "+LED_SCORE_LOG_FILE)
    new_filename = raw_input()
    if os.path.exists(new_filename):
        LED_SCORE_LOG_FILE      = new_filename
        BEST_LEDS               = None
        load_score_file()
        print("Loaded new file: "+str(new_filename))
    else:
        print("File does not exist - no changes applied.")

def increment_LED_quantity():
    global QTY_OF_BEST_LEDS_REQUIRED, BEST_LEDS
    if not USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED += 1
        BEST_LEDS               = None
        print("Increased QTY_OF_BEST_LEDS "+str(QTY_OF_BEST_LEDS_REQUIRED)+". Unchecked bounds.")
    elif USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED = default_QTY_OF_BEST_LEDS_REQUIRED()

def decrement_LED_quantity():
    global QTY_OF_BEST_LEDS_REQUIRED, BEST_LEDS
    if not USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED -= 1
        BEST_LEDS               = None
        print("Decreased QTY_OF_BEST_LEDS "+str(QTY_OF_BEST_LEDS_REQUIRED)+". Unchecked bounds.")
    elif USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED = default_QTY_OF_BEST_LEDS_REQUIRED()










# ======================================================================
# --- Draw simulation objects
# ======================================================================


class Tool:
    def __init__(self):
        global scale
        self.scale = scale
        self.cameras_vertices = camera_layout.getCameraPositions()
        self.tool = ToolSelector(self.scale)
        self.OLD_TOOLS_HERE = OldToolSelector_Untested(self.scale)

    def run( self ):
        # TODO: This is a hack to make running evaluations faster. An ideal implementation will refactor run.py module to separate GL from numerical evaluations.
        if glutGet(GLUT_INIT_STATE) == 1:
            draw_axes(self.scale, 2)
            draw_cameras(self.cameras_vertices)

        tool_selected = self.tool.selector()

        if not tool_selected:
            self.OLD_TOOLS_HERE.selector(self.scale, self.cameras_vertices)



class ToolSelector(object):
    """
        The fundamental conduit and selection mechanic to choose application behaviour; e.g. evaluations vs display vs tuning. and which behaviour strategy.
    """
    warned = False
    def __init__(self, scale):
        self.cached_tool = None
        # self.triangles, self.shape_name = get_target_shape_triangles()
        self.triangles, self.shape_name = WaveFront.get_target_shape(
                                                PARSE_OPTIONS.TARGET_SHAPE, 
                                                PARSE_OPTIONS.TARGET_SCALE, 
                                                eval(PARSE_OPTIONS.TARGET_TRANSLATION)
                                            )
        self.scale = scale

    def selector(self):
        result = True
        triangles       = self.triangles[:]
        shape_name      = self.shape_name

        kwords = {
            'all_leds': WaveFront.get_hardcoded_frame(self.scale)
                        # draw_dome(self.scale,
                        #           show_points=False,
                        #           show_led_spheres=False,
                        #           show_tris=False,
                        #           show_lines=False,
                        #           get_not_show_tris=False,
                        #           show_selected_leds=None)
        }
        # (1) Select Class Reference to Execute: ( See modes/illuminance/illuminance.py classes. )
        if self.cached_tool is None:
            switcher = {
                3: VertexIndexPositionEvaluator,
                4: EdgeXIndexPositionEvaluator,
                7: RawPositionEvaluator,
                8: VertexMappedPositionEvaluator,
                9: EdgeXMappedPositionEvaluator,
            }

            tool_class = switcher.get(PARSE_OPTIONS.EVALUATION_METRIC_MODE, None)
            # Instantiate Selected (1) Class
            self.cached_tool = tool_class(kwords) if tool_class is not None else None

            if self.cached_tool is None:
                result = False
                if ToolSelector.warned is False:
                    logging.warning("New Tool strategy failed to be selected and/or initialized.")
                    ToolSelector.warned = True

        # (3) Select Function Reference to Execute:
        if result:
            switcher = {
                1: self.cached_tool.display,
                2: self.cached_tool.evaluate,
                3: self.cached_tool.tune,
                4: self.cached_tool.sequence_runner,
            }
            func = switcher.get(PARSE_OPTIONS.EVALUATION, lambda x: None)

            #Execute (2) function on that (1) class:
            func(triangles)

        return result













class OldToolSelector_Untested(ToolSelector):
    """
        Evaluation (-m2) disabled in favour of cleaner code, more modern opengl code and illuminance evaluation methods. 
        Viewing (-m1) positions from file, etc. remains operable.
        Also see /modes/luminance/luminance.py
    """
    warned = False
    def selector(self, scale, camerasVertices):
        global camera_layout
        if not OldToolSelector_Untested.warned:
            print("Warning pre:v0.1.3 mode selected: Check runtime argument -e (--evaluation-metric-mode): " +str(PARSE_OPTIONS.EVALUATION_METRIC_MODE))
            print("--Untested features ahead--")
            OldToolSelector_Untested.warned = True
        triangles       = self.triangles[:]
        shape_name      = self.shape_name
        do_demo         = PARSE_OPTIONS.EVALUATION == 1
        do_evaluation   = PARSE_OPTIONS.EVALUATION == 2
        do_tune         = PARSE_OPTIONS.EVALUATION == 3

        # todo: This is a hack. Replace with polymorphic calls. Separate off the pre-V0.1.3 code that depend on options and globals instead of depend on properties file. Move luminance.py module code and unused reflectance modes - METRIC_MODE:0,1,4,5,6 out.
        if PARSE_OPTIONS.EVALUATION_METRIC_MODE == 0:

            if do_demo:
                draw_selected_leds( camerasVertices, triangles, shape_name)
            elif do_evaluation:
                print("No evaluation mode. Try demo mode (i.e. -m1)")
                pass
            elif do_tune:
                print("No tune mode. Try demo mode (i.e. -m1)")
                pass

        elif PARSE_OPTIONS.EVALUATION_METRIC_MODE == 1:       #EVALUATION_MODE_REFLECTANCE:
            self.cached_tool = self.cached_tool if self.cached_tool is not None else MeasureReflectanceIntoCameras()
            if do_demo:
                all_leds = draw_dome(scale, True)
                kwords = {
                    'LED_SCORE_LOG_FILE': LED_SCORE_LOG_FILE,
                    'CSV_METRIC_COLUMN_INDEX': 3,
                    'QTY_OF_BEST_LEDS_REQUIRED': QTY_OF_BEST_LEDS_REQUIRED,
                    'all_leds': all_leds,
                    'DO_EVALUATIONS': DO_EVALUATIONS,
                    'TARGET_ROTATIONS': TARGET_ROTATIONS,
                    'TARGET_TRIANGLES': TARGET_TRIANGLES,
                    'TARGET_ROTATION_DEGREES': TARGET_ROTATION_DEGREES,
                    'TARGET_ROTATION_AXIS': TARGET_ROTATION_AXIS,
                    'TARGET_SCALE': TARGET_SCALE,
                    'TARGET_TRANSLATION': TARGET_TRANSLATION,
                    'logged_score_to_file': logged_score_to_file,
                    'SELECT_BEST_LEDS': SELECT_BEST_LEDS,
                    'PARSE_OPTIONS': PARSE_OPTIONS,
                }
                self.cached_tool.display(triangles, shape_name, kwords)
            elif do_evaluation:
                #all_leds = draw_dome(scale, True)
                all_leds = draw_dome(scale,
                                     show_points=False,
                                     show_led_spheres=False,
                                     show_tris=False,
                                     show_lines=False,
                                     get_not_show_tris=False,
                                     show_selected_leds=None)
                kwords = {
                    'LED_SCORE_LOG_FILE': LED_SCORE_LOG_FILE,
                    'CSV_METRIC_COLUMN_INDEX': 3,
                    'QTY_OF_BEST_LEDS_REQUIRED': QTY_OF_BEST_LEDS_REQUIRED,
                    'all_leds': all_leds,
                    'DO_EVALUATIONS': DO_EVALUATIONS,
                    'TARGET_ROTATIONS': TARGET_ROTATIONS,
                    'TARGET_TRIANGLES': TARGET_TRIANGLES,
                    'TARGET_ROTATION_DEGREES': TARGET_ROTATION_DEGREES,
                    'TARGET_ROTATION_AXIS': TARGET_ROTATION_AXIS,
                    'TARGET_SCALE': TARGET_SCALE,
                    'TARGET_TRANSLATION': TARGET_TRANSLATION,
                    'logged_score_to_file': logged_score_to_file,
                    'SELECT_BEST_LEDS': SELECT_BEST_LEDS,
                    'PARSE_OPTIONS': PARSE_OPTIONS,
                }
                self.cached_tool.evaluate( camerasVertices, triangles, shape_name, camera_layout, kwords)
            elif do_tune:
                print("No tune mode. Try demo mode (i.e. -m1)")
                pass

        elif PARSE_OPTIONS.EVALUATION_METRIC_MODE == 2:     #EVALUATION_MODE_ILLUMINATION:
            #evaluate_illuminance_score( camerasVertices, triangles, shape_name )

            if do_demo:
                #draw_selected_leds( camerasVertices, triangles, shape_name)
                #evaluate_illuminance_score( camerasVertices, triangles, shape_name)
                print("This evaluation metric mode has been disabled and is marked for refactoring.")
            elif do_evaluation:
                print("This evaluation metric mode has been disabled and is marked for refactoring.")
            elif do_tune:
                print("No tune mode. Try demo mode (i.e. -m1)")
                pass
            GracefulShutdown.do_shutdown()


            
        # elif PARSE_OPTIONS.EVALUATION_METRIC_MODE == 4:     #EVALUATION_MODE_ILLUMINATION_MULTI:
        #     raise("This evaluation metric needs refactoring. To be refactored and tested. Now exiting.")
        #     sys.exit()
        #     all_leds        = draw_dome( scale , True )
        #     kwords = {
        #     	'LED_SCORE_LOG_FILE':LED_SCORE_LOG_FILE,
        #     	'CSV_METRIC_COLUMN_INDEX':3,
        #     	'QTY_OF_BEST_LEDS_REQUIRED':QTY_OF_BEST_LEDS_REQUIRED,
        #     	'all_leds':all_leds
        #     }
        #     evaluate_illuminance_score_multiple_result_file_set( updateable_line, camerasVertices, triangles, shape_name, 100000, kwords )
        #
        # elif PARSE_OPTIONS.EVALUATION_METRIC_MODE == 5:     #EVALUATION_MODE_ILLUMINATION_WEIGHT:
        #     ## --- evaluate_illuminance_score_result_file_set_tune_weights( updateable_line, camerasVertices, triangles, shape_name )
        #     #x = MeasureIlluminanceTuneWeights_AOS()
        #     #x.evaluate(updateable_line, camerasVertices, triangles, shape_name)
        #     raise("This evaluation metric needs refactoring. To be refactored and tested. Now exiting.")
        #     sys.exit()
        #
        # elif PARSE_OPTIONS.EVALUATION_METRIC_MODE == 6:     #EVALUATION_MODE_ILLUMINATION_WEIGHT:
        #     raise("This evaluation metric needs refactoring. To be refactored and tested. Now exiting.")
        #     sys.exit()
        #
        #     kwords = {}
        #     evaluate_minimised_distance_to_neighbours( camerasVertices, triangles, kwords )
















def draw_selected_leds( camerasVertices, triangles, shape_name ):
        best_LEDs   = get_best_leds_from_file()
        score       = get_best_score(best_LEDs)
        # leds        = draw_dome( scale , show_selected_leds=best_LEDs )
        leds = []
        qty_leds    = len(best_LEDs) if type(best_LEDs) is list else -1
        filename    = LED_SCORE_LOG_FILE if os.path.exists(LED_SCORE_LOG_FILE) else "(Press L to load file)"
        for tri in triangles:
            make_triangle_face( tri )
        
        string = []        
        string.append("Data file "+str(SCORE_DESCRIPTION)+": "+str(round(score,2)))
        string.append("Data file: "+str(filename))
        string.append("")
        string.append("LED Qty: "+str(qty_leds))
        string.append("Camera Qty: "+str(len(camerasVertices))+" "+str(CAMERA_SHORT_DESCRIPTION))
        #string.append("Camera Layout: "+str(CAMERA_SHORT_DESCRIPTION)+" (as shown not collected)")
        string.append("Target Model: "+str(shape_name))
        string.append("Target Scaling Factor: "+str(TARGET_SCALE))
        string.append("Target Translation: "+str(TARGET_TRANSLATION))
        string.append("Target Tri Qty: "+str(len(triangles)))
        string.reverse()
        for i in range(len(string)):
            draw_text(string[i],20,20+(i*15))



def get_target_shape_triangles():
    global TARGET_TRIANGLES, TARGET_SHAPE, TARGET_SHAPE_NAME, TARGET_TRANSLATION
    # Here be dragons..
    filename = "../models/dome/dome_c.obj"
    shape_name = "Dome"
    dome_scale = 1
    if TARGET_TRIANGLES == None:
        # At time of writing (05/2017), the hardcoded dome model's face mappings are not correct;
        # that model is incomplete. Therefore, we __must__ use the loaded dome from file, in order to evaluate.

        filename = TARGET_SHAPE if TARGET_SHAPE is not None else filename
        scale = TARGET_SCALE if TARGET_SCALE is not None else dome_scale
        TARGET_SHAPE_NAME = os.path.basename(TARGET_SHAPE) if TARGET_SHAPE is not None else shape_name
        # triangles = obj_model_reader.get_all_object_triangles(filename=filename, scale=scale, translation=TARGET_TRANSLATION)
        triangles = obj_model_reader.get_all_object_polyfaces( filename, scale, translation=TARGET_TRANSLATION )
        checkShapeValidity( triangles )
        TARGET_TRIANGLES = triangles
    return TARGET_TRIANGLES, TARGET_SHAPE_NAME



def load_score_file():
    global BEST_LED_DATA, BEST_LED_DATA_HEADER
    BEST_LED_DATA_HEADER    = file_io.read_in_csv_file_header_to_list(LED_SCORE_LOG_FILE)  if SELECT_BEST_LEDS else None
    BEST_LED_DATA           = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=True)  if SELECT_BEST_LEDS else None


def get_best_leds_from_file():
    global BEST_LEDS, BEST_LED_DATA
    if BEST_LEDS == None and BEST_LED_DATA == None: #1) BEST not loaded, and not loaded into DATA
        if os.path.exists(LED_SCORE_LOG_FILE):  #if: data file exists, then: load it into DATA
            load_score_file()
        else:                                   #else: if file doesn't exist, continue with no data.
            pass
    if BEST_LEDS == None and BEST_LED_DATA != None:
        if USE_SHADING_SCORE or USE_COVERAGE_SCORE:
            BEST_LEDS = get_sorted_column_from_result_file( BEST_LED_DATA, CSV_METRIC_COLUMN_INDEX, QTY_OF_BEST_LEDS_REQUIRED )
            # try_to_verify_symmetry( BEST_LED_DATA, column_index=3 )
    return BEST_LEDS


def get_best_score(best_LEDs):
    v = -1
    if best_LEDs != None: # Not loaded from file, then skip
        if USE_SHADING_SCORE:
            v = 0
            for i in best_LEDs:
                v += float(BEST_LED_DATA[i][ CSV_METRIC_COLUMN_INDEX ])     # Accumulate the reflection score per LED entry.
        elif USE_COVERAGE_SCORE:
            try:
                v = int(BEST_LED_DATA_HEADER[3].replace('coverage_error=',''))
            except ValueError:
                pass
        else:
            raise ValueError("Invalid scoring metric selected..")
    return v



