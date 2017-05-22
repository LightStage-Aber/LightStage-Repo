#!/bin/bash
errecho(){ >&2 echo $@; }

# Script Input arguments and defaults as globals:
if [ $# -ne 5 ]; then
    errecho "5 arguments required."
    errecho "Exiting."
    exit 1
fi


# Input arguments for Lettvin algorithm:
n=${1:-"45"}            # Num of LEDs
j=${2:-"0.0000001"}     # Jitter max value.
r=${3:-"0"}             # Num of rounds before exit, check usage.
i=${4:-"0"}             # Current iteration trial, for file output naming only.
directory=${5:-"test_output"} # Location for output .txt and .obj files.

timestamp=$(date -d "today" +"%Y-%m-%d_%H-%M")
file=$directory"/Output_Lettvin_Repulsion_positions_n"$n"_j"$j"_r"$r"_i"$i"__"$timestamp".txt"
file_ext=".obj"
path_to_run_evaluator="../../src/"


# Run the Lettvin Algorithm:
function run_lettvin_algorithm(){
    if [ -f "cpp/a.out" ]; then
        errecho "Begin Diffuse Algorithm: $n $j $r > $file"
        cpp/a.out $n $j $r > $file
        errecho "End Diffuse Algorithm"
    else
        errecho ""; errecho " -------------- "
        errecho "Binary not available. Try running 'make' from within ./cpp/ directory. Requires g++ compiler."
        errecho "Exiting."
        exit 1
    fi
    
    if [[ ! -f $file ]] || [[ $(wc -c < $file) -eq 0 ]]; then
        errecho ""; errecho " -------------- "
        errecho "Output result file is empty or not created."
        errecho "Exiting."
        exit 1    
    fi
}

# Extract and output the OBJ file:
function extract_and_create_OBJ_file(){
    errecho "Begin extract txt->obj"
    python helpers/parse_diffuse_results_to_obj_file.py $file $file_ext
    errecho "End extract txt->obj"
}

# Update the Properties File to load-in the new OBJ file:
function update_properties_file_to_load_OBJ(){
    objfile=$file""$file_ext
    path_to_properties="../../properties/default.properties"
    path_from_run_to_range_test_script="../exp/Lettvin_Repulsion/"
    #path_from_run_to_range_test_script="../../../PaulBourke_Geometry_DistributingPointsOnSphere/"
    errecho "Begin properties file update"
    python helpers/update_default-properties_file.py "DO_OVERWRITE" $objfile $path_to_properties $path_from_run_to_range_test_script
    errecho "End properties file update"
}

# Run the Evaluations:
function run_evaluations(){
    pwd=""$(pwd)""
    cd "$path_to_run_evaluator"
    errecho "Begin Py evaluations"
    python run.py -m2 -e7
    python run.py -m2 -e8
    python run.py -m2 -e9
    #python run.py -p $path_from_run_to_range_test_script""$objfile -s 8
    errecho "End Py evaluations"
    cd "$pwd"
}

function main(){
    run_lettvin_algorithm
    extract_and_create_OBJ_file
    update_properties_file_to_load_OBJ
    run_evaluations
}


# Begin
main
