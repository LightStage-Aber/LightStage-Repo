"""
    Module to create a latex table of results and output plots.

    THIS WILL WRITE/OVERWRITE A CSV FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1: Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2: should be the path to the input CSV file.
    arg3: should be the path to the output CSV file to re-write (and OVERWRITE, if it exists).
    arg3: should be the mapping type, as compared to values within 'column index 12' of the 'input CSV file'.
            For example: "Mapped to dome vertices (91 points)" or "Mapped to dome edges (10 points per edge. 3926 total points)" or "Raw Lettvin Positions"

    Example:
        python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "output_March19th2017.csv" "results_table_lettvin_March19th2017.tex" "Raw Lettvin Positions"
        python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "output_March19th2017.csv" "results_table_vertices_lettvin_March19th2017.tex" "Mapped to dome vertices (91 points)"
        python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "output_March19th2017.csv" "results_table_edges_lettvin_March19th2017.tex" "Mapped to dome edges (10 points per edge. 3926 total points)"


    Exception cases:
        === Unexpectedly giving a total N as N-1 ===
            Under the variants that map to mounting vertices and edges points, the reported quantity of N may not be equivalent to the Lettvin value of N.
            The cause of this can be where a single-mapped vertex mounting point is closest for two vertices output by the Lettvin algorithm.
            In this case, the (same) mounting point will be selected twice, yielding a total number of mounting points one less than expected.
"""

import sys, os, re
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
sys.path.insert(0,'../../../src/file_utils/')
import file_io


FULL_RANGE_OF_LED_QTYS = range(3,91,1)


def arguments():
    assert len(sys.argv) >= 5, "4 required arguments."
    DO_OVERWRITE = sys.argv[1]

    # Check input file exists:
    InputCSVFile_path = sys.argv[2]
    assert (os.path.exists(InputCSVFile_path))

    # Check output file exists:
    OutputCSVFile_path = sys.argv[3]

    MAPPING_TYPE = sys.argv[4]
    PATH_TO_OUTPUT = sys.argv[5]
    assert (MAPPING_TYPE != "" and MAPPING_TYPE != None)
    assert (PATH_TO_OUTPUT != None)

    return DO_OVERWRITE, InputCSVFile_path, OutputCSVFile_path, MAPPING_TYPE, PATH_TO_OUTPUT



def get_descriptive_stats_on_lettvin_results_highly_customised_function( matrix, MAPPING_TYPE ):
    d = {}
    for index in range(len(matrix)):
        # n44, j0.0000001, r0, i621, 7598, 0.0000001, 0.0000001, 0.269, 44, 1666.0939048602, 9.2560772492, 0.0214100642, Raw Lettvin Positions

        # Sets of 3 results (Raw,Edge,Vertices) would be identical. Let's do parse them all anyway, to ensure the Lettvin Stdev results are guaranteed to correspond. (alternative is index % 3 == 0)
        row = matrix[index]

        j = row[1]
        j = float(j.replace('j', ''))
        num = float(row[0].replace('n',''))
        #num = float(row[8])
        mapping_type = row[12]
        std = float(row[11])

        config_hash = str(num) + str(j) + str(mapping_type)
        res = [num, j, mapping_type, std]
        if mapping_type == MAPPING_TYPE:    # Restrict logged data to the specified mapping type.
            if config_hash in d: # if we had this config already, good, we need to accumulate the results from the 1000 iterations.
                d[config_hash].append(res) # add to the list of values for the 'n44+j0.001+r10000' config (for example).
            else:
                d[config_hash] = [res] # create a new list for values for the 'n44+j0.001+r10000' config (for example).
    return d




def get_stats(d):
    rows = []
    for key in d:
        values = np.array(d[key])

        #[num, j, mapping_type, std]
        column_index = 3
        vals = [float(x) for x in values[:, column_index]]
        n = int(float(values[0][0]))
        j = format(float(values[0][1]), '.8f')
        j = re.search('[0].[0]+[1]', j).group(0)
        mapping_type = values[0][2]
        vals = normalise_surface_values(n=int(n), vals=vals)
        
        mean = np.mean(vals)
        std = np.std(vals)
        median = np.median(vals)
        min_ =  min(vals)
        max_ = max(vals)
        iqrange = iqr(vals)
        norm_pvalue = "Inadequate quantity of values."
        statistic_value = "Inadequate quantity of values."
        if len(vals) > 20:
            # sample_vals = np.random.choice(vals, 200)
            # print "S: "+str(stats.normaltest( sample_vals ))
            # print "F: "+str(stats.normaltest( vals ))
            # print ("----- SIGNIF -------" if stats.normaltest( vals )[1] > 0.05 else "")
            norm_pvalue = stats.normaltest( vals )
                                # Omnibus test for normality, returns the P-value (2-sided chi squared probability)
                                # Based on D'Agostino and Pearson's [1], [2] test that combines skew and kurtosis to produce an omnibus test of normality
                                # References
                                # [1] D'Agostino, R. B. (1971), "An omnibus test of normality for moderate and large sample size", Biometrika, 58, 341-348
                                # [2] D'Agostino, R. and Pearson, E. S. (1973), "Tests for departure from normality", Biometrika, 60, 613-622
            norm_pvalue = format(float(norm_pvalue[1]), '.8f')
            statistic_value = format(float(norm_pvalue[0]), '.8f')
        row = [  str(n), str(j), str(min_), str(mean), str(std), str(norm_pvalue), str(statistic_value), str(median), str(iqrange), str(min_), str(max_), str(len(d[key])) , str(mapping_type) ]
        rows.append( row )
        
	
    header = ['N','J','Std. (Min)', 'Std. (Mean)','Std. (Std)','$Pv$ ($\chi^{2}$)', 'Statistic of Omnibus Test Normality (D\'Agostino, R. and Pearson, E. S. (1973) omnibus test of normality)','Median','IQR','Min','Max','Trials','Mapping Type']
    assert( len(rows) > 0 )
    rows = sorted(rows, key = lambda x: (x[0], x[1], x[9]))
    return rows,header



def iqr( x ):
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    return iqr


def normalise_surface_values(n=None, vals=[]):
	assert (n != None and type(n) == int), "Validate n: Should be the total quantity of lights in the evaluation trial."
	for i in range(len(vals)):
		x = vals[i]
		vals[i] = x/n
	return vals


def output_min_plots( x, name, std, ymax=0.25, ymin=0.15):
    plt.cla()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ylim(ymax=ymax, ymin=ymin)
    plt.ylabel("Lumens (Relative)", fontsize=18)
    plt.xlabel("Target Surface No." , fontsize=18)
    plt.tick_params(axis='both', which='major', labelsize=18)
    plt.tick_params(axis='both', which='minor', labelsize=18)
    plt.text(0.74, 0.95, std, fontsize=18, ha='center', va='center', transform=ax.transAxes)

    #plt.bar(range(len(x)), x, width=1.0, linewidth=0)
    plt.plot(range(len(x)), x, lw=0.5)
    plt.fill_between(range(len(x)), [0]*len(x), x, facecolor='blue', alpha=0.3)
    plt.grid(axis="both")
    fig.savefig(name+'.pdf', dpi=300)
    fig.savefig(name+'.png', dpi=80)


def get_min_per_mapping_type( matrix, MAPPING_TYPE, PATH_TO_OUTPUT ):
    for i in FULL_RANGE_OF_LED_QTYS:
        #     num = float(row[8])
        #     mapping_type = row[12]
        #     std = float(row[11])
        #     surfaces = [float(x) for x in best[15]]
        f = lambda x: x[12] == MAPPING_TYPE and x[8] == str(i)   # True for rows with for the matching 'mapping type' and number of positions as 'i'
        res = filter(f, matrix)
        res = np.array(res)

        # n4,j0.001,r0,i37,54,0.000968,0.001,0.816,4,151.57756515119047,0.8420975841732804,0.14450957805014208,Mapped to dome vertices (92 points),../exp/Lettvin_Repulsion/test_output/Results_RangeTest_2017-06-11_09-00/Output_Lettvin_Repulsion_positions_n4_j0.001_r0_i37__2017-06-11_09-12.txt.obj,VertexMappedPositionEvaluator,"[0.9232070380542445, 0.8790749123199136, 0.9209281567419345, 0.9389295114786695, 0.9301698575997107, 0.8864802670174678, 0.9662781956116059, 0.9482653957282561, 0.9488397566729544, 0.8479575114987195, 0.7884742992084808, 0.9715252593733834, 0.9331295165597684, 0.8587076357308933, 0.96350206527524, 1.086241042269239, 1.0766579938580794, 0.9499028444542421, 0.8817466883535785, 0.9711337445466306, 0.9331300215959495, 0.9885012782904552, 0.8587068968446332, 0.9331616543219596, 0.8817466752346723, 0.9711335260599496, 0.9120776237516437, 0.8587072287768498, 0.9635019911710939, 0.9635019274202014, 0.9698555834245832, 1.0594318646053889, 1.0506564739186717, 1.1370434798234683, 1.137043552800181, 1.0506568811911654, 0.8900527444157625, 0.969855639826461, 1.0210429816642486, 1.064557020827149, 1.0998189046488034, 1.0568815012162123, 1.0026281939623596, 0.9635019586819633, 0.9635017382917903, 0.9698551787678682, 0.8669180779905704, 0.8044980399600539, 0.8613409276965869, 0.6948560879104053, 0.8348047565146243, 0.8062426551611068, 0.7831080238340589, 0.8587065961564495, 0.7566858054083558, 0.9635018139790417, 0.9698553150476761, 0.8900523532860727, 0.7704875808718548, 1.0766573541202749, 0.948265331724889, 1.086241142346414, 1.0594319620434525, 0.9698555792272109, 0.9635021931030207, 0.9635020950316676, 1.0144523468760327, 1.036536693737455, 1.0779196594574003, 1.007643953580735, 0.8893130811899987, 0.8904956808326405, 0.9635020283153883, 0.963501840372727, 0.9698551842164396, 0.8669172055013283, 0.8817458631202553, 0.6557514680851906, 0.6948565855226285, 0.5956050750130797, 0.6651312792045255, 0.5886458095862824, 0.6024314977981527, 0.7375046537280954, 0.7962794398970889, 0.7884739886815763, 0.8587067883290713, 0.7576369106597931, 0.7031798435770312, 0.7743788905834768, 0.5507010241789108, 0.8891398385415814, 0.9662775786582302, 0.8587068472965312, 0.7566868322949751, 0.9635020953523251, 0.9635020786818099, 0.8587068351690599, 0.9124322907848423, 0.8253873574646051, 0.6024330134646034, 0.7375049046809408, 0.7566844639591648, 0.7884755708440245, 0.8587058534787915, 0.933161731942333, 0.9715251972180412, 0.8613404194924899, 0.9120776482079409, 0.5956053699271757, 0.520133204886168, 0.5268148896008376, 0.6024314767109813, 0.7375040607647632, 0.756686474370726, 0.8379949117286347, 0.8248213669875983, 0.7849455177911111, 0.78494542233844, 0.5855982228257871, 0.585598200565075, 0.5430679631256772, 0.70368800425491, 0.6053015695869317, 0.6115122532788257, 0.7566868758546247, 0.8587072193287737, 0.7831090622269752, 0.7831086996959705, 0.611782285827648, 0.7187774331558363, 0.6153789645887132, 0.6391953160662269, 0.6927712356394545, 0.8248221932713597, 0.9301706414666031, 0.8790752575962005, 0.9711335601514438, 0.9331299524240464, 0.8348050896701078, 0.665131677362797, 0.5886452670910208, 0.7831076273883796, 0.8587064310210801, 0.9635018487958459, 0.7884733604352023, 0.8248212276379461, 0.7031795184215874, 0.7576353853978317, 0.4526950999375806, 0.48881450784074293, 0.7138958213918765, 0.7706218918424792, 0.8069280143971531, 0.7811613905427, 0.7007566790563282, 0.5649010372982012, 0.6051736740151846, 0.7306932891275872, 0.8864805355781927, 0.8587066368139277, 0.8587063296797917, 0.8062435420793201, 0.9635018561191004, 0.9635019359270538, 0.9698554677774937, 0.9635018369523871, 0.8587065288197454, 0.7704859201860528, 0.5979322804106074, 0.7146377607397618, 0.7670132276143273, 0.8025194478272855, 0.7536791360833637, 0.7704854835945661, 0.757634740250834, 0.866918255914658, 0.8044989492541474, 0.8669181761313545, 0.9698554038494906]",2017-06-11-09-12-29,"[0, 1, 2, 3]"
        assert isinstance(res, np.ndarray) , "Filtered result expected as list. Found type: "+str(type(res))
        if len(res) == 0:
            print("Ignoring N=" + str(i))
            print( "N=" + str(i) + ")\tFiltered result expected of length GT 1. Found length: "+str(len(res)) + " , " + str(res) )
        else:
            index_min = np.argmin(res[:,11])
            best = res[index_min]
            surfaces = [float(x) for x in eval(best[15])]
            std = "Std. "+str(float(best[11]))+""
            name = "best_plot_" + str(i) + "_" + MAPPING_TYPE.replace(" ", "-").replace(".","")

            n=int(best[0].replace("n",""))
            surfaces = normalise_surface_values(n=n, vals=surfaces)
            std = "Std. "+str(np.std(surfaces))

            output_min_plots(surfaces, PATH_TO_OUTPUT + name, std)




def main():
    DO_OVERWRITE, InputCSVFile_path, OutputCSVFile_path, MAPPING_TYPE, PATH_TO_OUTPUT = arguments()
    matrix = file_io.read_in_csv_file_to_list_of_lists( InputCSVFile_path )
    d = get_descriptive_stats_on_lettvin_results_highly_customised_function( matrix, MAPPING_TYPE )
    rows, header = get_stats(d)
    get_min_per_mapping_type(matrix, MAPPING_TYPE, PATH_TO_OUTPUT)

    if DO_OVERWRITE == "DO_OVERWRITE":
        file_io.write_to_latex_table(rows, header, "", PATH_TO_OUTPUT + OutputCSVFile_path)
        file_io.write_to_csv([header]+rows, "", PATH_TO_OUTPUT + OutputCSVFile_path+".csv", asRows=True, doAppend=False)
    else:
        from tabulate import tabulate
        s = tabulate(rows, header, tablefmt="latex")
        print(s)

if __name__ == "__main__":
    main()
