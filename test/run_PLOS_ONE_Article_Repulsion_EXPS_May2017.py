default_path = "../src/"
import sys
import numpy as np
sys.path.insert(0, default_path)

import unittest
from run_PLOS_ONE_Article_Control_MC_EXPS_May2017 import GetActual_FromVertex
from file_utils import file_io


class _Config:
    SKIP_RAW_REPULSION_TESTS = False
    SKIP_VERTEX_REPULSION_TESTS = False
    SKIP_EDGE_REPULSION_TESTS = False


class Load_Lettvin_RepulsionData(object):
    """
    Utility mixin class to load in results files and extract corresponding filenames and std scores.
        1) Load in the results file.
            (format: n44,j0.001,r0,i1,235,0.000996,0.001,0.253,44,1666.2566239510388,9.256981244172438,0.0618355569228664,Raw Lettvin Positions,../../../PaulBourke_Geometry_DistributingPointsOnSphere/Results_RangeTest_2017-03-17_15-00/result_diffuse_positions_n44_j0.001_r0_i1__2017-03-17_15-05.txt.obj,MeasureLoadedLightPositions,"[9.195308610834058, 9.250042131907254, 9.306432942947051, 9.190310785466611, 9.271203291955135, 9.373116098498084, 9.257244726834978, 9.305311772287872, 9.263209736165523, 9.33271277462474, 9.236607143775071, 9.353657476304857, 9.196364760766444, 9.223682069680002, 9.214004752132, 9.302264147355121, 9.296292397917542, 9.263018850343206, 9.4073524453137, 9.291653403599225, 9.209343155442383, 9.1975850881833, 9.2600337988092, 9.173002146228367, 9.273054928011625, 9.277374473463698, 9.25717814383553, 9.23619654256007, 9.296095967513084, 9.265823015915865, 9.264493188509064, 9.329274593956274, 9.173869485817155, 9.175825303988331, 9.170441740575827, 9.284142465728682, 9.289320550995393, 9.098519457330452, 9.207926269799124, 9.15609082816997, 9.255424394911104, 9.305939819536475, 9.17460911735136, 9.309801704601089, 9.386144915350911, 9.17207742530888, 9.30552514860208, 9.219437397111546, 9.21364119364751, 9.336280496744891, 9.302691308933051, 9.278306394098912, 9.190370427231231, 9.308183240817222, 9.228463479187342, 9.172923503321973, 9.308547677270772, 9.242473705155147, 9.299903522008309, 9.252659065148231, 9.390539624763154, 9.158649422411727, 9.240699870530493, 9.276260451094391, 9.260178318415132, 9.232156241414625, 9.26140093334867, 9.2742442371666, 9.246704562682092, 9.310573584334904, 9.269673684662251, 9.291322188029971, 9.314419688050592, 9.243137022378257, 9.111706035580397, 9.37006903689155, 9.281987450361944, 9.203459894658279, 9.23414423330421, 9.158762168786645, 9.29111739794513, 9.239820393892566, 9.218007991095886, 9.298560288920989, 9.29427314158855, 9.29884489249122, 9.277919844859687, 9.298326162896519, 9.221712796343983, 9.23995012324926, 9.252250781509122, 9.237209578015236, 9.262111959053415, 9.301751316399615, 9.303803836588418, 9.305132372674832, 9.327209847398189, 9.284150140978072, 9.234690059060561, 9.28984782551271, 9.243428436727326, 9.275928885811837, 9.234118932498765, 9.215838435132673, 9.321834404667444, 9.033754145638678, 9.182538984934578, 9.234468134031701, 9.367295191973474, 9.28458808993, 9.271981564845193, 9.234034099733911, 9.332735912193762, 9.27185667530434, 9.319608807927487, 9.205223050955265, 9.203381705926143, 9.310752174602786, 9.238382524412211, 9.221325120215857, 9.251214741450399, 9.344506294956322, 9.131740939973922, 9.289150618766802, 9.117136686602972, 9.148612290345017, 9.36062923275773, 9.25236358287949, 9.222806513175431, 9.286246054271233, 9.281998280356449, 9.25394466893377, 9.313343985779733, 9.248577045478756, 9.277439737206938, 9.327349476559327, 9.150959405597572, 9.338791716315168, 9.297005568727549, 9.21367287326957, 9.218437205529677, 9.35753970205149, 9.150705962220837, 9.110601480873028, 9.252510803597556, 9.395950524345501, 9.225911303337472, 9.311606090922497, 9.310769815366038, 9.086005697921241, 9.299264617877341, 9.245714999475695, 9.27086761944784, 9.255403161493513, 9.21927574896872, 9.281583394621899, 9.245349583773239, 9.317695378733477, 9.259106804334081, 9.241660391388399, 9.268232088382286, 9.220953346806741, 9.230513394858882, 9.305608997549134, 9.223212572483039, 9.256838019917456, 9.211749155092619, 9.181740659868499, 9.306355161262696, 9.296861306444418, 9.328565097000746, 9.207129881186285, 9.266338865191985, 9.307774860501565, 9.154614856995895, 9.282909022169159, 9.219992532944131, 9.269538710587858, 9.224812229958092, 9.330793115470382]",2017-03-17-15-05-49,"[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]")
        2) For each N and J and all iterations of a MAPPING_TYPE, find the minimum Std. Get its corresponding filename and score.

        MAPPING_TYPE: should compare to values within 'column index 12' of the 'input CSV file'.
            For example: "Mapped to dome vertices (91 points)" or "Mapped to dome edges (10 points per edge. 3926 total points)" or "Raw Lettvin Positions"
    """
    class MAPPING_TYPE:
        RAW     = "Raw Lettvin Positions"
        VERTEX  = "Mapped to dome vertices (91 points)"
        EDGE    = "Mapped to dome edges (10 points per edge. 3926 total points)"

    def __init__(self, source_path, MAPPING_TYPE):
        self._load_in_matrix(source_path, MAPPING_TYPE)

    def _load_in_matrix(self, path, MAPPING_TYPE):
        matrix = file_io.read_in_csv_file_to_list_of_lists(path)
        self._matrix = self.__get_descriptive_stats_on_lettvin_results_highly_customised_function(matrix, MAPPING_TYPE)
        self._minimum_results = self._get_mins(self._matrix)

    def __get_descriptive_stats_on_lettvin_results_highly_customised_function(self, matrix, MAPPING_TYPE):
        d = {}
        for index in range(len(matrix)):
            # (format: n44,j0.001,r0,i1,235,0.000996,0.001,0.253,44,1666.2566239510388,9.256981244172438,0.0618355569228664,Raw Lettvin Positions,../../../PaulBourke_Geometry_DistributingPointsOnSphere/Results_RangeTest_2017-03-17_15-00/result_diffuse_positions_n44_j0.001_r0_i1__2017-03-17_15-05.txt.obj,MeasureLoadedLightPositions,"[9.195308610834058, 9.250042131907254, 9.306432942947051, 9.190310785466611, 9.271203291955135, 9.373116098498084, 9.257244726834978, 9.305311772287872, 9.263209736165523, 9.33271277462474, 9.236607143775071, 9.353657476304857, 9.196364760766444, 9.223682069680002, 9.214004752132, 9.302264147355121, 9.296292397917542, 9.263018850343206, 9.4073524453137, 9.291653403599225, 9.209343155442383, 9.1975850881833, 9.2600337988092, 9.173002146228367, 9.273054928011625, 9.277374473463698, 9.25717814383553, 9.23619654256007, 9.296095967513084, 9.265823015915865, 9.264493188509064, 9.329274593956274, 9.173869485817155, 9.175825303988331, 9.170441740575827, 9.284142465728682, 9.289320550995393, 9.098519457330452, 9.207926269799124, 9.15609082816997, 9.255424394911104, 9.305939819536475, 9.17460911735136, 9.309801704601089, 9.386144915350911, 9.17207742530888, 9.30552514860208, 9.219437397111546, 9.21364119364751, 9.336280496744891, 9.302691308933051, 9.278306394098912, 9.190370427231231, 9.308183240817222, 9.228463479187342, 9.172923503321973, 9.308547677270772, 9.242473705155147, 9.299903522008309, 9.252659065148231, 9.390539624763154, 9.158649422411727, 9.240699870530493, 9.276260451094391, 9.260178318415132, 9.232156241414625, 9.26140093334867, 9.2742442371666, 9.246704562682092, 9.310573584334904, 9.269673684662251, 9.291322188029971, 9.314419688050592, 9.243137022378257, 9.111706035580397, 9.37006903689155, 9.281987450361944, 9.203459894658279, 9.23414423330421, 9.158762168786645, 9.29111739794513, 9.239820393892566, 9.218007991095886, 9.298560288920989, 9.29427314158855, 9.29884489249122, 9.277919844859687, 9.298326162896519, 9.221712796343983, 9.23995012324926, 9.252250781509122, 9.237209578015236, 9.262111959053415, 9.301751316399615, 9.303803836588418, 9.305132372674832, 9.327209847398189, 9.284150140978072, 9.234690059060561, 9.28984782551271, 9.243428436727326, 9.275928885811837, 9.234118932498765, 9.215838435132673, 9.321834404667444, 9.033754145638678, 9.182538984934578, 9.234468134031701, 9.367295191973474, 9.28458808993, 9.271981564845193, 9.234034099733911, 9.332735912193762, 9.27185667530434, 9.319608807927487, 9.205223050955265, 9.203381705926143, 9.310752174602786, 9.238382524412211, 9.221325120215857, 9.251214741450399, 9.344506294956322, 9.131740939973922, 9.289150618766802, 9.117136686602972, 9.148612290345017, 9.36062923275773, 9.25236358287949, 9.222806513175431, 9.286246054271233, 9.281998280356449, 9.25394466893377, 9.313343985779733, 9.248577045478756, 9.277439737206938, 9.327349476559327, 9.150959405597572, 9.338791716315168, 9.297005568727549, 9.21367287326957, 9.218437205529677, 9.35753970205149, 9.150705962220837, 9.110601480873028, 9.252510803597556, 9.395950524345501, 9.225911303337472, 9.311606090922497, 9.310769815366038, 9.086005697921241, 9.299264617877341, 9.245714999475695, 9.27086761944784, 9.255403161493513, 9.21927574896872, 9.281583394621899, 9.245349583773239, 9.317695378733477, 9.259106804334081, 9.241660391388399, 9.268232088382286, 9.220953346806741, 9.230513394858882, 9.305608997549134, 9.223212572483039, 9.256838019917456, 9.211749155092619, 9.181740659868499, 9.306355161262696, 9.296861306444418, 9.328565097000746, 9.207129881186285, 9.266338865191985, 9.307774860501565, 9.154614856995895, 9.282909022169159, 9.219992532944131, 9.269538710587858, 9.224812229958092, 9.330793115470382]",2017-03-17-15-05-49,"[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]")

            # Sets of 3 results (Raw,Edge,Vertices) would be identical. Let's do parse them all anyway, to ensure the Lettvin Stdev results are guaranteed to correspond. (alternative is index % 3 == 0)
            row = matrix[index]

            j = row[1]
            j = float(j.replace('j', ''))
            num = float(row[0].replace('n', ''))
            # num = float(row[8])
            mapping_type = row[12]
            filename = row[13]
            std = float(row[11])

            config_hash = str(num) + str(j) + str(mapping_type)
            res = [num, j, mapping_type, std, filename]
            if mapping_type == MAPPING_TYPE:  # Restrict logged data to the specified mapping type.
                if config_hash in d:  # if we had this config already, good, we need to accumulate the results from the 1000 iterations.
                    d[config_hash].append(
                        res)  # add to the list of values for the 'n44+j0.001+r10000' config (for example).
                else:
                    d[config_hash] = [
                        res]  # create a new list for values for the 'n44+j0.001+r10000' config (for example).
        return d

    def _get_mins(self,matrix):
        res = {}
        for k in matrix.keys():
            values = np.array(matrix[k])
            # 1000x [n, j, mapping_type, std (unnormalised), path_to_obj]
            unnorm_std_column_index = 3
            path_to_obj_column_index = 4
            unnorm_stds = [float(x) for x in values[:, unnorm_std_column_index]]

            # Get the min std -- Note that all stds can be compared as each all have the same value of n.
            find_min_index = np.argmin(unnorm_stds)
            assert float(min(unnorm_stds)) == float(values[find_min_index][unnorm_std_column_index]), \
                                        "Found minimum index's " \
                                        "corresponding value ("+str(min(unnorm_stds))+") should be equal to the " \
                                        "found minimum value ("+str(values[find_min_index][unnorm_std_column_index])+")"

            # normalise the minimum std:
            n = int(float(values[0][0]))
            assert n > 0, "Number of LEDs, N should be GT 0."
            norm_std = float(matrix[k][find_min_index][unnorm_std_column_index]) / float(n)

            # get path to obj file:
            path_obj = matrix[k][find_min_index][path_to_obj_column_index]
            res[k] = [norm_std, path_obj]
        return res


class PLOSOneEXP_Repulsion_LettvinOnly(unittest.TestCase, Load_Lettvin_RepulsionData, GetActual_FromVertex):
    """
    This test suite requires:
        -  Running 'extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py' to expand the default results CSV file output.

    The evaluation mode e7-9 produces an output CSV file containing important data. However, it does not output
    the Lettvin parameter values (J, N, R and min-R). These are extracted from the associated test's obj filename.
    """
    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        GetActual_FromVertex.__init__(self, *args, **kwords)
        self._test_output_path  = "test/test_outputs/"
        self._file_path         = "" # Leave blank. The full file path *must be* specified within the individual unit tests.
        self.__error_threshold  = 0.00000000000001
        self.__source_path = "../results/Lettvin_RangeTest_Lambertian_Standard_Deviation_Results_91Vertices_44LEDS_1000iterations_Feb2017/output_March19th2017.csv"

    def __load_Profile_Results(self, MAPPING_TYPE):
        Load_Lettvin_RepulsionData.__init__(self, self.__source_path, MAPPING_TYPE)

    def __is_similar(self, actual, expected):
        return abs(float(actual) - float(expected)) < self.__error_threshold

    def __do_full_test(self, e=None):
        c = 0
        for k in self._minimum_results:
            c += 1
            result = self._minimum_results[k]
            expected = result[0]
            filepath = result[1]
            actual = self._get_actual(m=2, e=e, filename=filepath, n="Not Applicable", indexes_are_important=False, support_access=True)
            test_passed = self.__is_similar(actual, expected)

            if not test_passed:
                print("Failed for comparison with error threshold: " + str(self.__error_threshold)
                      + "\nFor values: Actual:(" + str(actual) + " == " + str(expected) + "):Expected"
                      + "\nFor hex: Actual:(" + str(float.hex(actual)) + " == " + str(
                    float.hex(expected)) + "):Expected"
                      + "\nFor types: Actual:(" + str(type(actual)) + " == " + str(type(expected)) + "):Expected"
                      + "\nFor length: Actual:(" + str(len(str(actual))) + " == " + str(
                    len(str(expected))) + "):Expected"
                      + "\nFor file: " + str(filepath) + "\nFor config: " + str(k))

            print(str(c) + ". " + str(test_passed) + " for " + str(k))
            self.assertTrue(test_passed)

    @unittest.skipIf(_Config.SKIP_RAW_REPULSION_TESTS, "Skipping raw repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_Raw(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.RAW)
        self.__do_full_test(e=7)

    @unittest.skipIf(_Config.SKIP_VERTEX_REPULSION_TESTS, "Skipping vertex repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_VertexMountings(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.VERTEX)
        self.__do_full_test(e=8)

    @unittest.skipIf(_Config.SKIP_EDGE_REPULSION_TESTS, "Skipping edge repulsion test..")
    def test_best_configs_of_repulsion_Lettvin_EdgeMountings(self):
        self.__load_Profile_Results(self.MAPPING_TYPE.EDGE)
        self.__do_full_test(e=9)





if __name__ == "__main__":
    # suite = unittest.TestLoader().loadTestsFromTestCase( PLOSOneEXP )
    # suite = unittest.TestSuite(); suite.addTest(Control_Evaluations('test_control_l91_using_hardcodedAOSMappedDome_True_is_same_as_test_control_l91_using_hardcodedAOSMappedDome_False'))
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)

    # Produce latex
    # Produce plots
