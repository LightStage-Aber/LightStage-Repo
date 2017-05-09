"""
    Module to create output plots (png, pdf) and latex tables (tex, csv) of the Lambertian light levels for the "Controls" and also "installed.csv" and "tweaker.csv" input CSV files.

    arg1: should be the path to the input CSV file.

    Example:
        python summary_latex_table_INSTALLED_config_std_results.py "DO_OVERWRITE" "lambertian_led_sets_VertexIndexPositionEvaluator.csv" "controls_result_table.txt"
        python summary_latex_table_INSTALLED_config_std_results.py "DO_OVERWRITE" "lambertian_led_sets_Edge10IndexPositionEvaluator.csv" "controls_result_table.txt"


"""

from __future__ import division
import sys, os, re
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
sys.path.insert(0,'../../src/file_utils/')
import file_io


def arguments():
    #print("Args: "+str(len(sys.argv))+" : "+str(sys.argv))
    assert len(sys.argv) == 4 # "Two argument required."
    
    DO_OVERWRITE = sys.argv[1]
    
    # Check input file exists:
    InputCSVFile_path = sys.argv[2]
    assert (os.path.exists(InputCSVFile_path))
        
    OutputCSVFile_path = sys.argv[3]    

    return InputCSVFile_path, DO_OVERWRITE, OutputCSVFile_path


def parse_to_table( matrix ):
	# [len(leds_vertex_set), len(all_leds)] + [total_set_lambertian_score, mean, stdev_set, median, iqrange, min_, max_] + extra_row_data + [surfaces] + [time.strftime("%Y-%m-%d-%H-%M-%S")] + led_index
	rows = []
	refd = {'l91.csv': 'V-Acc' ,'l92.csv': 'V-NoAcc' ,'odds.csv': 'Odd46' ,'evens.csv': 'Even46' ,'evens44.csv': 'Even44' , 'odds44.csv': 'Odd44' ,'edges_l3991.csv': 'E-NoAcc' ,'edges_l3893.csv': 'E-Acc' , 'installed_newlines_removed.csv': 'Inst' ,'tweaker.csv': 'Twkr'}

	for row in matrix:
	
		n = row[0]
		p = row[1]
		surfaces = [float(x) for x in eval(row[12])]
		surfaces = normalise_surface_values(n=float(row[0]), vals=surfaces)
		std = np.std(surfaces)
		filename = row[10].split("/")[-1]
		ref = refd[filename]
		
		res = [ref, str(n), str(p), str(std)+" \\\\%", filename]
		rows += [res] 
	header = ['\\textit{Ref.}','$N$','$P$','Std. \\\\%', 'Filename']
	return rows, header

def normalise_surface_values(n=92, vals=[]):
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


def get_min_per_mapping_type( matrix ):
    for row in matrix:
        #     num = float(row[8])
        #     mapping_type = row[12]
        #     std = float(row[11])
        #     surfaces = [float(x) for x in best[15]]
        surfaces = [float(x) for x in eval(row[12])]
        ns = row[0]+"_"+row[1]
        std = "Std. "+str(float(row[4]))
        min_ = float(row[7])
        max_ = float(row[8])
        # Get name of file, ignore directory names.
        filename = row[10].split("/")[-1]
        name = "control_plot_" + ns + "_" + filename.replace("/","").replace(".","-")
        
        surfaces = normalise_surface_values(n=float(row[0]), vals=surfaces)
        std = "Std. "+str(np.std(surfaces))
    	output_min_plots(surfaces, name, std )




def main():
	InputCSVFile_path, DO_OVERWRITE, OutputCSVFile_path = arguments()
	matrix = file_io.read_in_csv_file_to_list_of_lists( InputCSVFile_path )
	get_min_per_mapping_type( matrix )
	rows, header = parse_to_table( matrix )

	if DO_OVERWRITE == "DO_OVERWRITE":
		file_io.write_to_latex_table(rows, header, "", OutputCSVFile_path)
		file_io.write_to_csv([header]+rows, "", OutputCSVFile_path+".csv", asRows=True, doAppend=False)
	else:
		from tabulate import tabulate
		s = tabulate(rows, header, tablefmt="latex")
		print(s)

if __name__ == "__main__":
    main()
    
    
