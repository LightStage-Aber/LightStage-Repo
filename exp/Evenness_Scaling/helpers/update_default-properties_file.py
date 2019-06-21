"""
    Module to update the default.properties file.
    
    THIS WILL OVERWRITE THE PROPERTIES FILE, if and only if the first argument (arg1) is equal to "DO_OVERWRITE".

    arg1:
        Must be "DO_OVERWRITE", if the properties file is to be overwritten.
    arg2:
        The path to the default.properties file.
    arg3:
        Should be the search string to match. 
            e.g. light.results_output_file_path_prefix=
        Matches from start of line only.
        This line will be prepended with #  -- commented out.
    arg4:
        Should be the replacement value.  e.g. /file/path.txt
        The full line replacement would be: 
            "light.results_output_file_path_prefix=/file/path.txt"
        This value will be written into the default.properties file.
"""

import sys, os


def parse_arguments():
    DO_OVERWRITE = sys.argv[1]
    # Check properties file exists:
    filename = sys.argv[2]
    assert ( os.path.exists( filename ) ), "Properties file doesn't exist: "+str(filename)

    matcher = sys.argv[3] #"light.results_output_file_path_prefix="
    replace = sys.argv[4]
    return DO_OVERWRITE, filename, matcher, replace


def search_replace(filename, matcher, replace):
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
    return l

def do_output( filename, DO_OVERWRITE, l ):

    if DO_OVERWRITE == "DO_OVERWRITE":
        # Replace properties file. ENSURE BACKUP SEPARATELY
        f = open(filename,'w')
        for s in l:
            f.write( str(s) +"\n")
    else:
        for s in l:
            print(s)

def main():
    DO_OVERWRITE, filename, matcher, replace = parse_arguments()
    l = search_replace(filename, matcher, replace)
    do_output( filename, DO_OVERWRITE, l )


if __name__ == "__main__":
    main()