"""
    Module to update the csv file.
    	- This will update each line read from a CSV file. From each line, a corresponding filename string will be found and its file contents read into memory.
	    From the file's text content, the algorithm input parameter values will be extracted. 
    	These newly extracted parameter values will be used to write each new CSV line to the output file.

    THIS WILL WRITE/OVERWRITE A CSV FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1: Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2: should be the path to the input CSV file.
    arg3: should be the path to the output CSV file to re-write (and OVERWRITE, if it exists).

    Example Usage:
        python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "Results_RangeTest_2017-06-11_09-00/lambertian_led_sets_RawPositionEvaluator.csv" "outfile.csv" "../../"
"""
import sys, os, re
sys.path.insert(0,'../../../src/file_utils/')
import file_io

DO_OVERWRITE = sys.argv[1]

# Check input file obj exists:
InputCSVFile_path = sys.argv[2]
assert (os.path.exists(InputCSVFile_path)), "Input file does not exist: "+str(InputCSVFile_path)

# Check output csv file exists:
DefaultOutputCSV_path = sys.argv[3]
assert (len(DefaultOutputCSV_path) > 0)
if os.path.exists(DefaultOutputCSV_path):
    print("Warning output CSV file already exists.", DefaultOutputCSV_path)

ResultFilePathModifer = ""
if len(sys.argv) >= 5:
    ResultFilePathModifer = sys.argv[4]


def main():
    l = new_lettvin_output()

    if DO_OVERWRITE == "DO_OVERWRITE":
        # Append to file. ENSURE BACKUP SEPARATELY
        file_io.write_to_csv(l, "", DefaultOutputCSV_path, asRows=True, doAppend=True)
    else:
        for s in l:
            print(s)

def new_lettvin_output():
    # Read input CSV file.
    l = file_io.read_in_csv_file_to_list_of_lists(InputCSVFile_path, skip_header=False)

    for index in range(len(l)):
        row  = l[index]
        #'../../exp/Lettvin_Repulsion/test_output/Results_RangeTest_2017-06-11_09-00/Output_Lettvin_Repulsion_positions_n4_j0.001_r0_i1__2017-06-11_09-11.txt'
        # 18
        # Output Format:
        # [len(leds_vertex_set), len(all_leds)] + [total_set_lambertian_score, mean, unnormalised_stdev_set, median, iqrange, min_, max_]
        # + extra_row_data
        # + [surfaces]
        # + [time.strftime("%Y-%m-%d-%H-%M-%S")]
        # + led_index

        # Output Example:
        # ['4', '4', '151.53986350081018', '0.84188813056005662', '0.10429812098406073', '0.86745476128240961', '0.15849620692049948', '0.6162030837314685', '0.9956069540217636',
        #  'Raw Lettvin Positions',
        #  '../exp/Lettvin_Repulsion/test_output/Results_RangeTest_2017-06-11_09-00/Output_Lettvin_Repulsion_positions_n4_j0.001_r0_i1__2017-06-11_09-11.txt.obj',
        #  'RawPositionEvaluator',
        #  '[0.8610537581701401, 0.9638254039875358, 0.9054833293580674, 0.8363578237224524, 0.9231678987778617, 0.989084497615913, 0.8174288569290502, 0.96039608755861, 0.8690004302493031, 0.7934839434635632, 0.6921321820622393, 0.9116184430013313, 0.9872482860025329, 0.9191951126752245, 0.8487827546937233, 0.7721068980518846, 0.9335821271299078, 0.948674431375703, 0.9269445239456389, 0.7492591803410953, 0.6290399459521252, 0.649527207778008, 0.8468172728344108, 0.9026766685272736, 0.9572052640630111, 0.9459114181867755, 0.839561609193839, 0.9155896953350394, 0.8755853158419008, 0.9539791516901688, 0.772624981717324, 0.6203203998928657, 0.6439227077943017, 0.8329779838062326, 0.7045466770645186, 0.9249609049197203, 0.9276470421392372, 0.8991632472687757, 0.8212298529225632, 0.7234555367772799, 0.627928865515082, 0.6504227823537179, 0.721438228625944, 0.7333233044568016, 0.86741918811189, 0.9350030810371309, 0.975849935952295, 0.9471426825106208, 0.9009606204537306, 0.8524701864288176, 0.7941516418467727, 0.833512371363903, 0.8714693658842873, 0.9452569105428544, 0.9376146187682044, 0.9409019197193018, 0.8587550601939653, 0.736387292359979, 0.7241238737686888, 0.6550928920719776, 0.6455478630253908, 0.7103049065455249, 0.8140080462896537, 0.8991630284468448, 0.9355628711514612, 0.9355630201173734, 0.8293656738618898, 0.7773435168303485, 0.7359601041625242, 0.8386961941276014, 0.9306711833493901, 0.7241499346923356, 0.6957596229635963, 0.8041076195585688, 0.8947932670427018, 0.9062377996535078, 0.8970189165587483, 0.8862359711720853, 0.7708612330673462, 0.69318245252005, 0.6169706784784673, 0.7473440876758031, 0.7200950018855412, 0.8238577209252445, 0.7437502631472366, 0.9452024581362256, 0.9397872809601062, 0.8339050454773196, 0.8584544163655616, 0.6304787264004416, 0.7783567311636853, 0.7670891289315345, 0.7149772138171062, 0.8293649153120799, 0.9098655257746603, 0.9897826406000342, 0.9897826406000342, 0.9355628711514612, 0.8560677781421322, 0.9455050581549173, 0.9495581144539829, 0.9404707241455422, 0.8403749363323032, 0.9003375784897524, 0.9254725582825876, 0.9761356462525139, 0.9956069540217636, 0.8381890440270652, 0.8569724140071864, 0.623233701724268, 0.6521039144246032, 0.6523361668252328, 0.67194795678823, 0.6997005248439643, 0.8377222291686687, 0.859859563300255, 0.8816449578996731, 0.9237887388122453, 0.9932092786743065, 0.8528528668282986, 0.9217305363684296, 0.8820248186053459, 0.8788128932697178, 0.9475818643263961, 0.9782584474929952, 0.8889322003158698, 0.9355630201173731, 0.8991632472687758, 0.8991630284468448, 0.8829981014104382, 0.770252078091758, 0.945077262979245, 0.9508573486083354, 0.8901116099090668, 0.926499230379171, 0.9766379308143253, 0.8869260573509095, 0.9352606127556027, 0.8753488751871261, 0.8108382860372976, 0.7084049913312264, 0.7732914795590471, 0.9086805189985534, 0.928889064471095, 0.957740168384054, 0.9131314425902456, 0.9529504617050102, 0.9892738178330021, 0.9514681501621233, 0.9036664351175206, 0.9464610989522253, 0.9506950440398276, 0.9002149268238036, 0.7717138996439996, 0.7452099105953569, 0.740756852579396, 0.8364956388425768, 0.7529956387465647, 0.7874351156369903, 0.8259834751392893, 0.7951973762055465, 0.9475007776744269, 0.9248294885024491, 0.9594057606617303, 0.8809552158400997, 0.8190347209115103, 0.8921565765019267, 0.9112106007893938, 0.8477860359682973, 0.8674903344529292, 0.8849625974832365, 0.7500663175552994, 0.6878702140977188, 0.6534846311587744, 0.6542722331294186, 0.6162030837314685, 0.6400109580402225, 0.6306051758885471, 0.7422045898483012, 0.8300762791598526]',
        #  '2017-06-11-09-11-12', '0', '1', '2', '3']

        n_result = int(row[0])
        total_lam_score_result = float(row[2])
        mean_result = float(row[3])
        unnormalised_stdev_set = float(row[4])
        [mappingType, filePathObj, evaluatorType] = row[9:12]
        surfaces = [float(x) for x in eval(row[12])]
        timestamp = row[13]
        led_indexes = [int(x) for x in row[14:]]

        s = row[10]  #Lettvin output obj file name, containing configuration values.
        n = re.search('n[0-9.]+', s).group(0)
        j = re.search('j[0-9.]+', s).group(0)
        r = re.search('r[0-9.]+', s).group(0)
        i = re.search('i[0-9.]+', s).group(0)

        # Read in Lettvin output results file, and extract relevant result data:
        s = s.replace(".obj", "")
        [rounds, jiggle_dV_from, jiggle_dV_to, min_R] = get_lettvin_output_file_result_values(s)

        # Update the output row with new config and result data, in order to output to file.
        l[index]    = [n,j,r,i] + [int(rounds), float(jiggle_dV_from), float(jiggle_dV_to), float(min_R)] + [int(n_result)] + [float(total_lam_score_result)] + [mean_result] + [float(unnormalised_stdev_set)] + [mappingType, filePathObj, evaluatorType] + [surfaces] + [timestamp] + [led_indexes]
        # Format: n , j , r , i , rounds, jiggle_dV_from, jiggle_dV_to, minR, n(from Py), totalScore(from Py), mean(from Py), unNormalisedStd(from Py),   MappingType, FilenamePathObj, EvalType, "[SurfaceScores]" , Timestamp(from Py), LED_Indexes(from Py),
        # (format: n44,j0.001,r0,i1,235,0.000996,0.001,0.253,44,1666.2566239510388,9.256981244172438,0.0618355569228664,Raw Lettvin Positions,../../../PaulBourke_Geometry_DistributingPointsOnSphere/Results_RangeTest_2017-03-17_15-00/result_diffuse_positions_n44_j0.001_r0_i1__2017-03-17_15-05.txt.obj,MeasureLoadedLightPositions,"[9.195308610834058, 9.250042131907254, 9.306432942947051, 9.190310785466611, 9.271203291955135, 9.373116098498084, 9.257244726834978, 9.305311772287872, 9.263209736165523, 9.33271277462474, 9.236607143775071, 9.353657476304857, 9.196364760766444, 9.223682069680002, 9.214004752132, 9.302264147355121, 9.296292397917542, 9.263018850343206, 9.4073524453137, 9.291653403599225, 9.209343155442383, 9.1975850881833, 9.2600337988092, 9.173002146228367, 9.273054928011625, 9.277374473463698, 9.25717814383553, 9.23619654256007, 9.296095967513084, 9.265823015915865, 9.264493188509064, 9.329274593956274, 9.173869485817155, 9.175825303988331, 9.170441740575827, 9.284142465728682, 9.289320550995393, 9.098519457330452, 9.207926269799124, 9.15609082816997, 9.255424394911104, 9.305939819536475, 9.17460911735136, 9.309801704601089, 9.386144915350911, 9.17207742530888, 9.30552514860208, 9.219437397111546, 9.21364119364751, 9.336280496744891, 9.302691308933051, 9.278306394098912, 9.190370427231231, 9.308183240817222, 9.228463479187342, 9.172923503321973, 9.308547677270772, 9.242473705155147, 9.299903522008309, 9.252659065148231, 9.390539624763154, 9.158649422411727, 9.240699870530493, 9.276260451094391, 9.260178318415132, 9.232156241414625, 9.26140093334867, 9.2742442371666, 9.246704562682092, 9.310573584334904, 9.269673684662251, 9.291322188029971, 9.314419688050592, 9.243137022378257, 9.111706035580397, 9.37006903689155, 9.281987450361944, 9.203459894658279, 9.23414423330421, 9.158762168786645, 9.29111739794513, 9.239820393892566, 9.218007991095886, 9.298560288920989, 9.29427314158855, 9.29884489249122, 9.277919844859687, 9.298326162896519, 9.221712796343983, 9.23995012324926, 9.252250781509122, 9.237209578015236, 9.262111959053415, 9.301751316399615, 9.303803836588418, 9.305132372674832, 9.327209847398189, 9.284150140978072, 9.234690059060561, 9.28984782551271, 9.243428436727326, 9.275928885811837, 9.234118932498765, 9.215838435132673, 9.321834404667444, 9.033754145638678, 9.182538984934578, 9.234468134031701, 9.367295191973474, 9.28458808993, 9.271981564845193, 9.234034099733911, 9.332735912193762, 9.27185667530434, 9.319608807927487, 9.205223050955265, 9.203381705926143, 9.310752174602786, 9.238382524412211, 9.221325120215857, 9.251214741450399, 9.344506294956322, 9.131740939973922, 9.289150618766802, 9.117136686602972, 9.148612290345017, 9.36062923275773, 9.25236358287949, 9.222806513175431, 9.286246054271233, 9.281998280356449, 9.25394466893377, 9.313343985779733, 9.248577045478756, 9.277439737206938, 9.327349476559327, 9.150959405597572, 9.338791716315168, 9.297005568727549, 9.21367287326957, 9.218437205529677, 9.35753970205149, 9.150705962220837, 9.110601480873028, 9.252510803597556, 9.395950524345501, 9.225911303337472, 9.311606090922497, 9.310769815366038, 9.086005697921241, 9.299264617877341, 9.245714999475695, 9.27086761944784, 9.255403161493513, 9.21927574896872, 9.281583394621899, 9.245349583773239, 9.317695378733477, 9.259106804334081, 9.241660391388399, 9.268232088382286, 9.220953346806741, 9.230513394858882, 9.305608997549134, 9.223212572483039, 9.256838019917456, 9.211749155092619, 9.181740659868499, 9.306355161262696, 9.296861306444418, 9.328565097000746, 9.207129881186285, 9.266338865191985, 9.307774860501565, 9.154614856995895, 9.282909022169159, 9.219992532944131, 9.269538710587858, 9.224812229958092, 9.330793115470382]",2017-03-17-15-05-49,"[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]")

    return l

# def old_lettvin_output():
#     # Read input CSV file.
#     l = file_io.read_in_csv_file_to_list_of_lists(InputCSVFile_path, skip_header=False)
#
#     for index in range(len(l)):
#         row  = l[index]
#         #'../../../PaulBourke_Geometry_DistributingPointsOnSphere/Results_RangeTest_2017-02-19_16-00/result_diffuse_positions_n44_j0.00001_r10000_i4__2017-02-19_16-33.txt.obj',
#         #'../../exp/Lettvin_Repulsion/test_output/Results_RangeTest_2017-06-11_09-00/Output_Lettvin_Repulsion_positions_n4_j0.001_r0_i1__2017-06-11_09-11.txt'
#         s = row[10]  #Lettvin output obj file name, containing configuration values.
#         print len(row)
#         print row
#         sys.exit()
#         n = re.search('n[0-9.]+', s).group(0)
#         j = re.search('j[0-9.]+', s).group(0)
#         r = re.search('r[0-9.]+', s).group(0)
#         i = re.search('i[0-9.]+', s).group(0)
#         mean = float(row[1]) / float(180)
#
#         # Read in Lettvin output results file, and extract relevant result data:
#         s = "../" + s.replace(".obj", "")
#         [rounds, jiggle_dV_from, jiggle_dV_to, min_R] = get_lettvin_output_file_result_values(s)
#
#         # Update the output row with new config and result data, in order to output to file.
#         surfaces    = [float(x) for x in row[6:186]]
#         led_indexes = [int(x) for x in row[187:]]
#         l[index]    = [n,j,r,i] + [int(rounds), float(jiggle_dV_from), float(jiggle_dV_to), float(min_R)] + [int(row[0])] + [float(row[1])] + [mean] + [float(row[2])] + row[3:6] + [surfaces] + [row[186]] + [led_indexes]
#
#     return l


def get_lettvin_output_file_result_values( filename ):
    """ Get lettvin output file result values:
    """
    l = file_io.read_file_to_list( ResultFilePathModifer + filename )
    rounds          = re.search('=[0-9]+/', l[0]).group(0).replace('=', '').replace('/', '')
    jiggle_dV_from  = re.search('=[0-9\-e+.]+', l[1]).group(0).replace('=', '')
    jiggle_dV_to    = re.search('/[0-9\-e+.]+', l[1]).group(0).replace('/', '')
    min_R           = re.search('=[0-9\-e+.]+', l[2]).group(0).replace('=', '')

    res = [rounds, jiggle_dV_from, jiggle_dV_to, min_R]
    try:
        valid = all( [type(float(x)) is float for x in res])
        assert valid , "Parsing of Lettvin output results file led to an unexpected data type in %r" % filename 
    except ValueError as e:
        print( "Parsing of Lettvin output results file led to an unexpected data type in %r" % filename )
        print( "Extracted values: %r" % res )
        raise
    return res


if __name__ == "__main__":
    main()
