"""
    Module to update the default.properties file.
        - Replace the output directory.
    
    THIS WILL OVERWRITE THE PROPERTIES FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1:
        Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2:
        Should be the path to the default.properties file.
        Relative to current working directory.
        This value will be used to open the file for reading and overwriting contents.
    arg3:
        Should be the path to the results output file.
        Relative to the "run.py" application.
        This value will be written into the default.properties file and intepreted by the "run.py".
"""

import sys, os

DO_OVERWRITE = sys.argv[1]
# Check properties file exists:
assert ( os.path.exists( sys.argv[2] ) ), "Properties file doesn't exist: "+str(sys.argv[2])


matcher = "light.results_output_file_path_prefix="
filename = sys.argv[2]
replace = sys.argv[3]


# Read Properties Files, in order to update it.
# Find every line starting with the "@matcher", insert new line with updated "@matcher+@replace", comment out original "@matcher" line.
l = []
with open(filename, 'rb') as f:
    for line in f:
        if line.strip().startswith(matcher):
            l.append( str(matcher)+str(replace) )
            l.append( "#"+line.strip() )
        else:
            l.append( line.strip() )


if DO_OVERWRITE == "DO_OVERWRITE":
    # Replace properties file. ENSURE BACKUP SEPARATELY
    f = open(filename,'w')
    for s in l:
        f.write( str(s) +"\n")
else:
    for s in l:
        print s