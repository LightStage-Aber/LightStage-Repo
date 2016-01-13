from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import math, sys, time;     currentMillis = lambda: int(round(time.time() * 1000))
from optparse import OptionParser

import dome_obj_data
import file_io
import obj_model_reader
import score_even_surface_coverage_lighting as surface_coverage_metric
from coverage_datastructure import accumulated_coverage_datastructure
from updateable_line import Updateable_Line
from vector_maths import *
import analytical_reflection_models as reflect_models
import key_events



# ======================================================================
# --- Parameterised config update
# ======================================================================
parser = OptionParser()
parser.add_option("-m", "--mode",
                  action="store", dest="EVALUATION", default=1, metavar='NUM', type=int,
                  help="Specify the tool mode. 1=Display mode (default). 2=Evaluation mode.")
parser.add_option("-p", "--target-path",
                  action="store", dest="TARGET_SHAPE", default=None, metavar='PATH', type=str,
                  help="Specify the path to an .obj file of the target model. For example: '../dome_c.obj'. Default is a mini-dome.")
parser.add_option("-s", "--target-scale",
                  action="store", dest="TARGET_SCALE", default=1.0, metavar='SCALE', type=float,
                  help="Specify the target model scaling factor. - Default=1.0")
parser.add_option("-t", "--target-translation",
                  action="store", dest="TARGET_TRANSLATION", default='(0,0,0)', metavar='(x,y,z)', type=str,
                  help="Specify the target model translation. i.e. move -1 on Y-axis: '(0,-1,0)'")
parser.add_option("-c", "--camera-layout",
                  action="store", dest="CAMERA_LAYOUT", default=1, metavar='NUM', type=int,
                  help="Specify the camera layout. 1=Realistic bias (default). 2=Even bias.")
parser.add_option("-l", "--qty-leds",
                  action="store", dest="LEDS_QTY", default=42, metavar='NUM', type=int,
                  help="Specify the number of LEDs in range(0-92). Default is 42. *Note: Currently not loaded from data file.*")
parser.add_option("-r", "--load-result-file",
                  action="store", dest="LED_SCORE_LOG_FILE", default=None, metavar='PATH', type=str,
                  help="Specify the path to an LED score result data file. For example: '../led_scores_xxx.csv'. ")
options,args = parser.parse_args()



# Program's Config
SELECT_BEST_LEDS            = True if options.EVALUATION == 1 else False
QTY_OF_BEST_LEDS_REQUIRED   = options.LEDS_QTY;   default_QTY_OF_BEST_LEDS_REQUIRED = lambda: options.LEDS_QTY
realistic_bias              = True if options.CAMERA_LAYOUT == 1 else False
TARGET_SHAPE                = options.TARGET_SHAPE          #None
TARGET_SCALE                = options.TARGET_SCALE          #0.01
TARGET_TRANSLATION          = eval(options.TARGET_TRANSLATION)    #(0,-3,0)


# Display Configuration for Scoring
USE_SHADING_SCORE       = True
USE_COVERAGE_SCORE      = not USE_SHADING_SCORE
SCORE_DESCRIPTION       = "Intensity Score" if USE_SHADING_SCORE else "Coverage Error"
CSV_METRIC_COLUMN_INDEX = 1 if USE_SHADING_SCORE else 3



# Camera Configuration:
even_bias = not realistic_bias
CAMERA_POSITION_DESCRIPTION = "Even bias. 6 cameras. 4 on equator 90 degrees apart. 2 at the poles." if even_bias else "Realistic bias. 6 cameras. 3 on equator 90 degrees apart. 2 at the front offset by 5 degrees. 1 top-down."
CAMERA_SHORT_DESCRIPTION = "Realistic bias" if realistic_bias else "Even bias"

# Material Configuration:
MAT_SHININESS = 1
DIFFUSE_SHADING_DESCRIPTION  = "Shading Diffuse: Lambertian cosine"
SPECULAR_SHADING_DESCRIPTION = "Shading Specular: Blinn-Phong with material shininess exponent: "+str(MAT_SHININESS)
SHADING_LIGHT_DESCRIPTION    = "Light RGBA Channel(s): A single channel without multiplier is used, equivalent to RGBA(1,0,0,1)"
SHADING_MATERIAL_DESCRIPTION = "Material RGBA Channel(s): A single channel without multiplier is used, equivalent to RGBA(1,0,0,1)"


# Extra Detailed Program Configs:
DO_EVALUATIONS      = True
DRAW_REFLECTION_RAY = True
DRAW_INCIDENT_RAY   = True
DRAW_CAMERA_REFLECTION_RAY  = True
DRAW_TRI_SHAPE_NORMALS      = False
DRAW_TRIS           = True
DRAW_GROUND         = False
o = (0,0,0)
scale = 8
TARGET_ROTATIONS = 6
TARGET_ROTATION_AXIS = (0,1,0)
TARGET_ROTATION_DEGREES=(360/TARGET_ROTATIONS)
cameraPos = (0,0,scale+1.5)




log_score            = file_io.file_writer(path="../",filename="led_scores_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".csv") if not SELECT_BEST_LEDS else None
log_meta_data        = file_io.file_writer(path="../",filename="led_meta_data_"+time.strftime("%Y-%m-%d-%H-%M-%S")+".txt") if not SELECT_BEST_LEDS else None
LED_SCORE_LOG_FILE   = options.LED_SCORE_LOG_FILE if options.LED_SCORE_LOG_FILE != None and os.path.exists(options.LED_SCORE_LOG_FILE) else ""
logged_score_to_file = False
loggable             = []
DATA_HEADER          = ["led_num","reflection_score","tri_hit_score"]
BEST_LEDS            = None
TARGET_TRIANGLES     = None
TARGET_SHAPE_NAME    = ''
BEST_LED_DATA_HEADER = None
BEST_LED_DATA        = None
#BEST_LED_DATA_HEADER = file_io.read_in_csv_file_header_to_list(LED_SCORE_LOG_FILE)  if SELECT_BEST_LEDS else None
#BEST_LED_DATA        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=True)  if SELECT_BEST_LEDS else None


#kieferTriangles = obj_model_reader.get_all_object_triangles( filename="../../models/plant_kiefer/kiefer.obj", scale=1 )
illumination_coverage_datastructure = accumulated_coverage_datastructure()


        
# ======================================================================
# --- Live config update
# ======================================================================
HELP = {}
HELP['r'] = "Toggle scoring (maximised intensity / maximised target coverage)."
HELP['c'] = "Toggle camera positioning."
HELP['t'] = "Toggle test evaluation mode to verify angles and scoring.\n\t- Use Left-Arrow and Right-Arrow to change LED.\n\t- Use y/h/u/j/i/k to update incident ray X,Y,Z coordinate."
HELP['g'] = "Toggle wireframe ground"
HELP['n'] = "Toggle target normals"
HELP['l'] = "Load new score file."
HELP['+'] = "Increase LEDs selected. (Shading Score only. Unchecked bounds.)"
HELP['-'] = "Decrease LEDs selected. (Shading Score only. Unchecked bounds.)"
HELP['Up']    = "Zoom in / Wheel-up"
HELP['Down']  = "Zoom out / Wheel-down"
HELP['F1']    = "Display help."
HELP['Space'] = "Toggle scene rotation."
HELP['Esc']   = "Exit."
print("\nPress F1 to display help.")

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
    elif k == 'g':
        toggle_wireframe_ground()
    elif k == 'n':
        toggle_target_normals()
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
    USE_SHADING_SCORE       = not USE_SHADING_SCORE   
    USE_COVERAGE_SCORE      = not USE_SHADING_SCORE
    SCORE_DESCRIPTION       = "Shading Score" if USE_SHADING_SCORE else "Coverage Error"
    CSV_METRIC_COLUMN_INDEX = 1 if USE_SHADING_SCORE else 3
    BEST_LEDS               = None
    if USE_COVERAGE_SCORE:
        QTY_OF_BEST_LEDS_REQUIRED = default_QTY_OF_BEST_LEDS_REQUIRED()
    msg = "Toggled scoring to Shading Score" if USE_SHADING_SCORE else "Toggled scoring to Coverage Score"
    print(msg)


def toggle_camera_setup():
    global realistic_bias, even_bias, CAMERA_SHORT_DESCRIPTION
    realistic_bias = not realistic_bias
    even_bias = not realistic_bias
    CAMERA_SHORT_DESCRIPTION = "Realistic bias" if realistic_bias else "Even bias"
    msg = "Toggled camera bias to realistic" if realistic_bias else "Toggled camera bias to even"
    print(msg)

def toggle_wireframe_ground():
    global DRAW_GROUND
    DRAW_GROUND = not DRAW_GROUND
    msg = "Toggled wireframe ground on" if DRAW_GROUND else "Toggled wireframe ground off"
    print(msg)

def toggle_target_normals():
    global DRAW_TRI_SHAPE_NORMALS
    DRAW_TRI_SHAPE_NORMALS = not DRAW_TRI_SHAPE_NORMALS
    msg = "Toggled target normals on" if DRAW_TRI_SHAPE_NORMALS else "Toggled target normals off"
    print(msg)


def toggle_test_evaluation_mode():
    global SELECT_BEST_LEDS, DO_EVALUATIONS, DRAW_GROUND
    SELECT_BEST_LEDS = not SELECT_BEST_LEDS
    DO_EVALUATIONS = False if not SELECT_BEST_LEDS else True
    DRAW_GROUND = False if not SELECT_BEST_LEDS else DRAW_GROUND
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

def get_target_shape_triangles():
    global TARGET_TRIANGLES, TARGET_SHAPE, TARGET_SHAPE_NAME
    if TARGET_TRIANGLES == None:
        if TARGET_SHAPE == None:
            triangles = draw_dome( TARGET_SCALE , False, False, False, False, True )
            TARGET_SHAPE_NAME = "Dome"
            obj_model_reader.apply_translate( triangles, translate_tris=TARGET_TRANSLATION )
        else:
#            TARGET_SHAPE        = "../../models/Flower/plants3.obj"
#            TARGET_SCALE        = 0.01
#            TARGET_TRANSLATION  = (0,-3,0)
            TARGET_SHAPE_NAME   = os.path.basename(TARGET_SHAPE)
            triangles           = obj_model_reader.get_all_object_triangles( filename=TARGET_SHAPE, scale=TARGET_SCALE )
            obj_model_reader.apply_translate( triangles, translate_tris=TARGET_TRANSLATION )
        TARGET_TRIANGLES        = triangles
#    shape_name = "Plant Kiefer"
#    triangles = kieferTriangles
    
    checkShapeValidity( TARGET_TRIANGLES )
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
            l = BEST_LED_DATA
            l = sorted(l,key=lambda x: x[CSV_METRIC_COLUMN_INDEX], reverse=True)
            l = l[:QTY_OF_BEST_LEDS_REQUIRED]   # Get top n positions
            l = np.array(l)[:,0]                # Get only position data
            l = list(l)                         # Convert back to py list
            l = [int(x) for x in l]             # Convert strings to ints.
            BEST_LEDS = l
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



    
    

def draw( updateable_line ):
        global cameraPos, scale
        
        draw_axes(8, 2)
        if DRAW_GROUND:
            draw_ground()
        camerasVertices = draw_cameras( cameraPos )
        triangles, shape_name = get_target_shape_triangles()
        
        if SELECT_BEST_LEDS:
            draw_selected_leds( updateable_line, camerasVertices, triangles, shape_name )
        else:
            draw_and_evaluate_leds( updateable_line, camerasVertices, triangles, shape_name )
            

def draw_selected_leds( updateable_line, camerasVertices, triangles, shape_name ):
        best_LEDs   = get_best_leds_from_file()
        score       = get_best_score(best_LEDs)
        leds        = draw_dome( scale , show_selected_leds=best_LEDs )
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


def draw_and_evaluate_leds( updateable_line, camerasVertices, triangles, shape_name ):
        global cameraPos, scale, logged_score_to_file, loggable, TARGET_ROTATIONS
        string = []        
        drawTextString = []
        l,r,d = 0,0,0
        leds = draw_dome( scale , True )
        
        startTime = currentMillis()
        if not DO_EVALUATIONS:
            leds                = [updateable_line.get_point()] # Use reflections from single light selected by arrow-keys.
            TARGET_ROTATIONS    = 1                             # Remove rotations.
            triangles           = TARGET_TRIANGLES[:10]
            shape_name          = "Test Tri"
        
        reflection_score = 0
        triangleHit_score = 0
        for led_num in range(len(leds)):
            led_score = 0                               # The accumulated scaled reflection-angle-to-each-camera-from-specular-angle score.
            led_tri_hit_score = 0                       # The number of tris the led has hit.
            led = leds[led_num]
            
            
            if DO_EVALUATIONS:
                progress_complete   = str(round((led_num+1)*(100.0/len(leds)),0))
                progress_time       = str(round(((currentMillis()-startTime)/1000.0)/60,2))
                print(progress_complete+"% at "+progress_time+" mins")
            
            for rotation_num in range(TARGET_ROTATIONS):  
                if DO_EVALUATIONS:
                    triangles = rotate_triangles(triangles, axis=TARGET_ROTATION_AXIS, degrees=TARGET_ROTATION_DEGREES)
                for tri_num in range(len(triangles)):
                    tri = triangles[tri_num]
                    make_triangle_face( tri )
                    c  = find_center_of_triangle( tri )
                    n1 = find_perpendicular_of_triangle( tri )              # Get normal of current tri plane.
                    l, r    = reflect_no_rotate( c, led, n1 )
                    """ usage of l and r require a prior-translate to c.
                    """
                    if is_front_facing_reflection(tri, l, r):       #Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )
                        for cam_num in range(len(camerasVertices)):
                            cam = camerasVertices[cam_num]
                            if is_front_facing_reflection_to_camera(tri, cam):
                                
                                draw_reflection_to_camera( [cam], tri )
                                draw_incident_ray(c, l)
                                draw_reflection_ray(c, r)
                                view = np.subtract(cam, c)    #reposition relative to center of incident surface.
                                rad,d = get_angle_from_reflection_to_camera(c, r, view)
                                
                                blinn_spec           = reflect_models.BlinnPhong_specular(incident_vector=l, view_vector=view, surface_norm=n1, shininess_exponent=MAT_SHININESS)
                                lamb_diffuse         = reflect_models.Lambert_diffuse( incident_vector=l, surface_norm=n1 )
                                
                                this_led_score       = lamb_diffuse + blinn_spec
                                led_score           += this_led_score
                                
                                if DO_EVALUATIONS:
                                    coverage_score  = this_led_score
                                    illumination_coverage_datastructure.add( coverage_score, led_num, tri_num)
                                else:
                                    drawTextString.append("Camera "+str(cam_num)+": "+str(round(d,2))+"d;    "+str(round(blinn_spec,2))+" + "+str(round(lamb_diffuse,2))+" = "+str(round(this_led_score,2)) )

                        led_tri_hit_score +=1

            if DO_EVALUATIONS:
                if not logged_score_to_file:
                    loggable.append( [led_num, led_score, led_tri_hit_score] )
                reflection_score += led_score
                triangleHit_score += led_tri_hit_score
        
#        print "Time taken: "+str(round((currentMillis()-startTime)/1000.0,2))+" seconds"
#        print("Coverage Score",best_score, best_leds)
        if DO_EVALUATIONS:
            led_to_tri_reflection_map           = illumination_coverage_datastructure.get()
            best_score, best_config, best_leds  = surface_coverage_metric.get_led_configuration_with_best_coverage( 
                                                                              led_to_tri_reflection_map, 
                                                                              len(triangles), 
                                                                              max_quantity_of_leds_required=QTY_OF_BEST_LEDS_REQUIRED, 
                                                                              max_depth=2,
                                                                              max_steps=10, 
                                                                              ignore_tri_lighting_error=True, 
                                                                              ignore_led_lighting_error=True )
            for i in range(len(loggable)):
                led_n = loggable[i][0]
                is_selected = 1 if led_n in best_leds else 0
                loggable[i].append( is_selected )
            
            DATA_HEADER.append( "coverage_error="+str(best_score))
            
            endTime = currentMillis()
            if not logged_score_to_file:
                loggable = [DATA_HEADER]+loggable
            
                string.append("Logged led scores to file: "+str(log_score.get_filepath()))
                string.append("Logged meta data to file: "+str(log_meta_data.get_filepath()))
                string.append("Target Model: "+str(shape_name))
                string.append("Target Scaling Factor: "+str(TARGET_SCALE))
                string.append("Target Translation: "+str(TARGET_TRANSLATION))
                string.append("Reflection Score: "+str(reflection_score))
                string.append("Triangle Hit Qty Score: "+str(triangleHit_score))
                string.append("Triangle Coverage Error Score: "+str(best_score))
                string.append("Quantity of LEDs for Coverage Error: "+str(QTY_OF_BEST_LEDS_REQUIRED))
                string.append("Time taken: "+str(round((endTime-startTime)/1000.0,2))+" seconds")
                string.append("Quantity of LEDs: "+str(len(leds)))
                string.append("Quantity of Tris: "+str(len(triangles)))
                string.append("Quantity of Cameras: "+str(len(camerasVertices)))
                string.append("Camera position description: "+CAMERA_POSITION_DESCRIPTION)
                string.append("Camera positions: "+str(cameraPos))
                string.append("Quantity of Target Rotations: "+str(TARGET_ROTATIONS))
                string.append("Target Axis Rotation: "+str(TARGET_ROTATION_AXIS)+", "+str(TARGET_ROTATION_DEGREES)+" degrees")
                string.append( DIFFUSE_SHADING_DESCRIPTION  )
                string.append( SPECULAR_SHADING_DESCRIPTION )
                string.append( SHADING_LIGHT_DESCRIPTION    )
                string.append( SHADING_MATERIAL_DESCRIPTION )
                
                log_score.write_to_csv_rows( loggable )
                log_meta_data.write_to_file_list(string, append_newline=True)
                logged_score_to_file = True
                print "-------------------"
                for s in string:
                    print s
                print "-------------------"
                sys.exit()
        else:
            led_display_header = "LED "+str(updateable_line.get_index())+" Degrees ReflectRay-to-Cam; Specular Intensity + Diffuse Intensity = Total Intensity"
            drawTextString.append("-"*len(led_display_header))
            drawTextString.append(led_display_header)
            drawTextString.reverse()
            for i in range(len(drawTextString)):
                draw_text(drawTextString[i],20,20+(i*15))
        













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
    print_debug = False
    glTranslate( c[0],c[1],c[2] )
    if print_debug: draw_triangle_face( [o, r, view] )
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

def draw_reflection_rays(c, l, r):
    draw_reflection_ray(c, r)
    draw_incident_ray(c, l)
    
def draw_reflection_ray(c, r):
    if DRAW_REFLECTION_RAY:
        glTranslatef( c[0],c[1],c[2] )
        draw_line(r, o, 5)
        glTranslatef( -c[0],-c[1],-c[2] )

def draw_incident_ray(c, l):
    if DRAW_INCIDENT_RAY:
        glTranslatef( c[0],c[1],c[2] )
        draw_line(l, o, 1)
        glTranslatef( -c[0],-c[1],-c[2] )

def draw_reflection_to_camera( cameras, tri ):
        if DRAW_CAMERA_REFLECTION_RAY:
            for c in cameras:
                    face_center = find_center_of_triangle( tri )
                    draw_line( c, face_center )             
                    





def draw_cameras( cameraPos ):
        size = 0.8
        
        if realistic_bias:
            cam0 = rotate_vector( cameraPos, (1,0,0), -5 )        # Add front-facing camera (just below equator)
            cam1 = rotate_vector( cameraPos, (1,0,0), 5 )         # Add front-facing camera (just above equator)
            cam2 = rotate_vector( cameraPos, (0,1,0), 90 )      # Add position on the equator
            cam3 = rotate_vector( cam2, (0,1,0), 90 )           # Add position on the equator
            cam4 = rotate_vector( cam3, (0,1,0), 90 )           # Add position on the equator
            cam5 = rotate_vector( cameraPos, (1,0,0), -90 )     # Add top-down camera
            camerasVertices = [cam0, cam1, cam2, cam3, cam4, cam5]
        elif even_bias:
            cam1 = rotate_vector( cameraPos, (0,1,0), 0 )       # Add position on the equator
            cam2 = rotate_vector( cameraPos, (0,1,0), 90 )      # Add position on the equator
            cam3 = rotate_vector( cam2, (0,1,0), 90 )           # Add position on the equator
            cam4 = rotate_vector( cam3, (0,1,0), 90 )           # Add position on the equator
            cam5 = rotate_vector( cameraPos, (1,0,0), -90 )     # Add top-down camera
            cam6 = rotate_vector( cameraPos, (1,0,0), 90 )      # Add bottom-up camera
            camerasVertices = [cam1, cam2, cam3, cam4, cam5, cam6]

        for c in camerasVertices:
            glPushMatrix()
            glTranslatef( c[0],c[1],c[2] )
            glutSolidCube( size )
            glPopMatrix()
        return camerasVertices
        

                

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

def checkShapeValidity( triangles ):
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

        
# ----------------------------------------------
        
def make_triangle_face( tri = [( 0.0, 0.0, 0.0), (-1.0,-1.0,-1.0), (1.0,1.0,-1.0)] ):
        if DRAW_TRIS:
            draw_triangle_face( tri )
        if DRAW_TRI_SHAPE_NORMALS:
            draw_normal_line( tri )
        

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

