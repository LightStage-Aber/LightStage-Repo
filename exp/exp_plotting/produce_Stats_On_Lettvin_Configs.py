"""
    Module to calculate and extract stats over the Lettvin Parameter Configs.

    THIS WILL WRITE/OVERWRITE A CSV FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1: Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2: should be the path to the input CSV file.
    arg3: should be the path to the output CSV file to re-write (and OVERWRITE, if it exists).
"""

import sys, os, re
import numpy as np
sys.path.insert(0,'../../src/file_utils/')
import file_io


def arguments():
    assert len(sys.argv) >= 4, "Three required arguments."
    DO_OVERWRITE = sys.argv[1]

    # Check input file exists:
    InputCSVFile_path = sys.argv[2]
    assert (os.path.exists(InputCSVFile_path))

    # Check output file exists:
    OutputCSVFile_path = sys.argv[3]
    return OutputCSVFile_path, InputCSVFile_path, DO_OVERWRITE



def main():
    OutputCSVFile_path, InputCSVFile_path, DO_OVERWRITE = arguments()

    matrix = file_io.read_in_csv_file_to_list_of_lists( InputCSVFile_path )
    rows = get_descriptive_stats_on_lettvin_results_highly_customised_function(matrix)

    if DO_OVERWRITE == "DO_OVERWRITE":
        file_io.write_to_csv(rows, "", OutputCSVFile_path, asRows=True, doAppend=False)
    else:
        for r in rows:
            print(r)

def get_descriptive_stats_on_lettvin_results_highly_customised_function( matrix ):
    d = {}
    columns = ["rounds", "j_from", "j_to", "min_r"]
    for index in range(len(matrix)):
        if index % 3 == 0: # Take only the first of 3 sets of results (Raw,Edge,Vertices). For the Lettvin results, they each would be identical.
            row = matrix[index]
            n = row[0]
            j = row[1]
            r = row[2]
            i = row[3]
            config_hash = str(n)+str(j)+str(r)

            rounds = int(row[4])
            j_from = float(row[5])
            j_to = float(row[6])
            min_r = float(row[7])
            res = [rounds, j_from, j_to, min_r]

            if config_hash in d: # if we had this config already, good, we need to accumulate the results from the 1000 iterations.
                d[config_hash].append(res) # add to the list of values for the 'n44+j0.001+r10000' config (for example).
            else:
                d[config_hash] = [res] # create a new list for values for the 'n44+j0.001+r10000' config (for example).

    rows = get_stats(d, columns)
    return rows


def get_stats(d, columns):
    rows = []
    for key in d:            # for each entry
        values = np.array(d[key])
        output_row = []
        qty = (len(values))
        for i in range(len(values[0])):    # for each column in the list.
            mean = np.mean(values[:,i])
            median = np.median(values[:,i])
            min_ =  min(values[:,i])
            max_ = max(values[:,i])
            iqrange = iqr(values[:,i])
            std = np.std(values[:,i])
            col = columns[i]
            o = [col,mean,std,median,iqrange,min_,max_]
            output_row += o
        sep_key = separate_key(key)
        rows.append(sep_key + [qty] + output_row)
    header = ['n','j','r'] + ['qty'] + (['col','mean','std','median','iqrange','min_','max_'])*len(values[0])
    return [header]+rows

def separate_key( key ):
    #n45j0.0001r10000
    n = re.search('n[0-9\-e+.]+j', key).group(0).replace('n', '').replace('j','')
    j = re.search('j[0-9\-e+.]+r', key).group(0).replace('j', '').replace('r','')
    r = re.search('r[0-9\-e+.]+', key).group(0).replace('r','')
    return [int(n),float(j),int(r)]

def iqr( x ):
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    return iqr

if __name__ == "__main__":
    main()
