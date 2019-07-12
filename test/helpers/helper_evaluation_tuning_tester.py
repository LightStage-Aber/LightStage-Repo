from __future__ import print_function
import sys
from helper_std_pipe_capture import captured_stdout
from options import getPropertiesFile, get_parsed_commandline_options
import run



class _Config:
    DEBUG = True
    DEBUG_STDOUT_CAPTURE = False


class SetupEvaluator:

    def options(self, m, e):
        PARSE_OPTIONS, PARSE_ARGS = get_parsed_commandline_options()
        PARSE_OPTIONS.EVALUATION = m
        PARSE_OPTIONS.EVALUATION_METRIC_MODE = e
        PARSE_OPTIONS.TARGET_SHAPE = "../models/dome/dome_c.obj"
        PARSE_OPTIONS.TARGET_SCALE = 1

    def execute_get_first_match_from_stdout(self, match):
        with captured_stdout() as stdout:
            x = run.LightStageApp()
            x.main()
        output_strings = str(stdout.getvalue()).strip().split("\n")
        stdout.close()
        if _Config.DEBUG_STDOUT_CAPTURE:
            map(print, output_strings)

        matchers = [match]
        lines = [s for s in output_strings if any(xs in s for xs in matchers)]
        assert len(lines) >= 1, "No match found within standard output for string: '%s'" % (str(match))
        res = lines[0].replace(match,"")
        return res


class Setup_FromIndex_Evaluator(SetupEvaluator):

    def properties(self, output_path_prefix, input_filename, number_of_leds, indexes_are_important_HCD, use_support_access, edge_qty):
        getPropertiesFile()['LightIndexPositions']['results_file.csvfilename'] = input_filename
        getPropertiesFile()['LightIndexPositions']['results_file.results_output_file_path_prefix'] = output_path_prefix
        getPropertiesFile()['LightIndexPositions']['results_file.column_number'] = 3
        getPropertiesFile()['LightIndexPositions']['results_file.number_of_leds'] = number_of_leds

        getPropertiesFile()['FrameModel']['frame.withsupportaccess'] = use_support_access
        getPropertiesFile()['FrameModel']['frame.indexes_are_important'] = indexes_are_important_HCD
        getPropertiesFile()['FrameModel']['frame.number_of_vertices_per_edge'] = edge_qty
        getPropertiesFile()['FrameModel']['frame.support_access_vertices_to_remove'] = 1

        getPropertiesFile()['LightOutput']['light.output_intensity_from_index.enforce_default'] = True
        getPropertiesFile()['LightOutput']['light.output_intensity_from_index.default_value'] = 1.0


class Setup_FromVertex_Evaluator(SetupEvaluator):

    def properties(self, output_path_prefix, input_filename, number_of_leds, indexes_are_important_HCD, use_support_access, edge_qty):
        getPropertiesFile()['LightPositions']['light.objfilename'] = input_filename
        getPropertiesFile()['LightPositions']['light.results_output_file_path_prefix'] = output_path_prefix
        getPropertiesFile()['LightPositions']['light.scale'] = 8

        getPropertiesFile()['FrameModel']['frame.withsupportaccess'] = use_support_access
        getPropertiesFile()['FrameModel']['frame.indexes_are_important'] = indexes_are_important_HCD
        getPropertiesFile()['FrameModel']['frame.number_of_vertices_per_edge'] = edge_qty
        getPropertiesFile()['FrameModel']['frame.support_access_vertices_to_remove'] = 1

        getPropertiesFile()['LightOutput']['light.output_intensity_from_index.enforce_default'] = True
        getPropertiesFile()['LightOutput']['light.output_intensity_from_index.default_value'] = 1.0
        


class GetActual_FromVertex(object):
    def __init__(self, *args, **kwords):
        self._test_output_path  = ""
        self._file_path         = ""
        self._setup = Setup_FromVertex_Evaluator()
        self._error_threshold  = 0.0000001

    def _get_actual(self, m=None, e=None, filename=None, n=None, indexes_are_important=None, support_access=None, edge_qty=10):
        self._setup.options(
            m=m,
            e=e
        )
        self._setup.properties(
            output_path_prefix = self._test_output_path,
            input_filename=self._file_path + str(filename),
            number_of_leds=n,
            indexes_are_important_HCD=str(indexes_are_important),
            use_support_access=str(support_access),
            edge_qty=edge_qty
        )
        actual = self._setup.execute_get_first_match_from_stdout("Finished with normalised standard deviation:")
        if _Config.DEBUG:
            sys.stderr.write(str(actual)+" ... ")
        return float(actual)
    
    def _is_similar(self, actual, expected):
        r = abs(float(actual) - float(expected)) < self._error_threshold
        return r

class GetActual_FromIndex(GetActual_FromVertex):
    def __init__(self):
        self._test_output_path  = ""
        self._file_path         = ""
        self._setup = Setup_FromIndex_Evaluator()
        self._error_threshold  = 0.0000001
