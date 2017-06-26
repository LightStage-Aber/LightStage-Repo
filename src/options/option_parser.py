from optparse import OptionParser

__CACHED_PARSE_OPTIONS, __CACHED_PARSE_ARGS = None, None

# ======================================================================
# --- Parameterised config update
# ======================================================================
def get_parsed_commandline_options():
    global __CACHED_PARSE_OPTIONS, __CACHED_PARSE_ARGS

    if __CACHED_PARSE_OPTIONS is None or __CACHED_PARSE_ARGS is None:
        parser = OptionParser()
        parser.add_option("-m", "--mode",
                          action="store", dest="EVALUATION", default=1, metavar='NUM', type=int,
                          help="Specify the tool mode. 1=Display mode (default). 2=Evaluation mode. 3=Tune-evaluation mode.")
        parser.add_option("-e", "--evaluation-metric-mode",
                          action="store", dest="EVALUATION_METRIC_MODE", default=0, metavar='NUM', type=int,
                          help="Specify the evaluation metric mode." + \
                               "'-e0' =Default. (-m1) Display best selected LEDs from -e1 result file. (-m2) No action." + \
                               "'-e1' =Use Reflectance Measures. " + \
                               "'-e2' =Use Illuminance Measure Search (Lambertian only). " + \
                               "'-e3' =Use Illuminance Measure (Lambertian only) to evaluate 'Single' loaded file; depends on properties file values: see '[LightIndexPositions]' and '[FrameModel]' - (file, qty, column, etc.) in 'default.properties' file." + \
                               "'-e4' =Use Illuminance Measure (Lambertian only) to evaluate 'Single Edge(10:3926)' loaded file; depends on properties file values: see '[LightIndexPositions]'" + \
                               "'-e7' =Use Illuminance Measure (Lambertian only) to evaluate 'RAW' vertex position file; depends on properties file values: see '[LightPositions]'" + \
                               "'-e8' =Use Illuminance Measure (Lambertian only) to evaluate 'Vertex Mappings' vertex position file; depends on properties file values: see '[LightPositions]'" + \
                               "'-e9' =Use Illuminance Measure (Lambertian only) to evaluate 'Edge(10) Mappings' vertex position file; depends on properties file values: see '[LightPositions]'" + \
                               "")
        parser.add_option("-p", "--target-path",
                          action="store", dest="TARGET_SHAPE", default=None, metavar='PATH', type=str,
                          help="Specify the path to an .obj file of the target model. For example: '../models/dome/dome_c.obj'. Default is a mini-dome of 180 tris, 92 vertices.")
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
                          action="store", dest="LEDS_QTY", default=44, metavar='NUM', type=int,
                          help="Specify the number of LEDs to show in demo and to evaluate in range(0-92). Default is 44. *Note: This value is not currently recalled from any results files.*")
        parser.add_option("-r", "--load-result-file",
                          action="store", dest="LED_SCORE_LOG_FILE", default=None, metavar='PATH', type=str,
                          help="Specify the path to an LED score result data file. For example: '../led_scores_xxx.csv'. ")
        parser.add_option("-k", "--reflectance-score",
                          action="store", dest="DIFFUSE_REFLECTANCE_ONLY", default=1, metavar='NUM', type=int,
                          help="Specify the reflectance model scorings used in evaluation mode. 1=Lambert's diffuse only. 2=Lambert's diffuse and Blinn-Phong's specular (default).")
        parser.add_option("-d", "--display-evaluation-metric",
                          action="store", dest="DISPLAY_EVALUATION_METRIC_OPTION", default=1, metavar='NUM', type=int,
                          help="Specify the evaluation metric display mode from result file. 1=Use Index Column 1 Scores (default). 2=Use Index Column 3 Scores (Lambertian only).")
        __CACHED_PARSE_OPTIONS, __CACHED_PARSE_ARGS = parser.parse_args()

    return __CACHED_PARSE_OPTIONS, __CACHED_PARSE_ARGS
