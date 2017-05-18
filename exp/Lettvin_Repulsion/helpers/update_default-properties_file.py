"""
    Module to update the default.properties file. 
    
    THIS WILL OVERWRITE THE PROPERTIES FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1: Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2: should be the path to the obj file.
    arg3: should be the path to the default.properties file to read/re-write.
    arg4: should be the relative path from the "run.py" application to the root of the obj file path (arg2). This will be written to the default.properties file and intepreted by the "run.py".
"""

import sys, os

DO_OVERWRITE = sys.argv[1]

# Check input file obj exists:
LightPositionsObjFile_path = sys.argv[2]
assert( os.path.exists( LightPositionsObjFile_path ) )

# Check properties file exists:
DefaultProperties_path = sys.argv[3]
assert( os.path.exists( DefaultProperties_path ) )

# Get the relative path from "src/run.py" to the obj file.
RelativeResults_path = sys.argv[4]


# Read Properties Files, in order to update it.
# Find "light.objfilename=" line, insert new line with updated "light.objfilename=", comment out original "light.objfilename=" line.
l = []
with open(DefaultProperties_path, 'rb') as f:
    for line in f:
        if line.strip().startswith("light.objfilename="):
            l.append( "light.objfilename="+str(RelativeResults_path)+str(LightPositionsObjFile_path) )
            l.append( "#"+line.strip() )
        else:
            l.append( line.strip() )


if DO_OVERWRITE == "DO_OVERWRITE":
    # Replace properties file. ENSURE BACKUP SEPARATELY
    f = open(DefaultProperties_path,'w')
    for s in l:
        f.write( str(s) +"\n")
else:
    for s in l:
        print s
