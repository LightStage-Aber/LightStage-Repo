#!/bin/bash
errecho(){ >&2 echo $@; }

# ---------------------------------------------------------------------------------------
# Run example as:
#           -- ./run_target_evenness_scaling_trial.sh "../models/ico_sphere/ico_sphere.obj"
# ---------------------------------------------------------------------------------------

# Script Input arguments and defaults as globals:
if [ $# -ne 1 ]; then
    errecho "1 arguments required." 
    errecho "e.g.    ./run_target_evenness_scaling_trial.sh \"../models/ico_sphere/ico_sphere.obj\""
    errecho "Exiting."
    exit 1
fi


# Input arguments:
target_object_filepath=${1:-"../models/ico_sphere/ico_sphere.obj"}    # 

timestamp=$(date -d "today" +"%Y-%m-%d_%H-%M")
path_to_run_evaluator="../../src/"

# Update the Properties File
# function update_properties_file(){
    # path_to_properties="../../properties/default.properties"
    # errecho "Begin properties file update"
    # python helpers/update_default-properties_file.py "DO_OVERWRITE" $path_to_properties "light.output_intensity_from_index.default_value=" $target_object_filepath
    # errecho "End properties file update"
    # ""
# }

# Run the Evaluations:
function run_evaluations(){
    pwd=""$(pwd)""
    cd "$path_to_run_evaluator"
    errecho "Begin Py evaluations"
    python run.py -p $target_object_filepath -m1 -e3
    #python run.py -p $path_from_run_to_range_test_script""$objfile -s 8
    errecho "End Py evaluations"
    cd "$pwd"
}

function main(){
    # update_properties_file
    run_evaluations
}


# Begin
main
