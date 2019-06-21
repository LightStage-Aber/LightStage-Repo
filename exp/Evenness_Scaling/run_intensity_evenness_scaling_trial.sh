#!/bin/bash
errecho(){ >&2 echo $@; }

# ---------------------------------------------------------------------------------------
# Run example as:
#           -- ./run_evenness_scaling_trial.sh 1.0 "exp/Evenness_Scaling/test_output/"
# ---------------------------------------------------------------------------------------

# Script Input arguments and defaults as globals:
if [ $# -ne 1 ]; then
    errecho "1 arguments required." 
    errecho "e.g.    ./run_evenness_scaling_trial.sh 1.0"
    errecho "Exiting."
    exit 1
fi


# Input arguments:
intensity_value=${1:-"1.0"}    # Num of LEDs

timestamp=$(date -d "today" +"%Y-%m-%d_%H-%M")
path_to_run_evaluator="../../src/"

# Update the Properties File
function update_properties_file(){
    path_to_properties="../../properties/default.properties"
    errecho "Begin properties file update"
    python helpers/update_default-properties_file.py "DO_OVERWRITE" $path_to_properties "light.output_intensity_from_index.default_value=" $intensity_value
    errecho "End properties file update"
}

# Run the Evaluations:
function run_evaluations(){
    pwd=""$(pwd)""
    cd "$path_to_run_evaluator"
    errecho "Begin Py evaluations"
    python run.py -p "../models/ico_sphere/ico_sphere.obj" -m2 -e3
    #python run.py -p $path_from_run_to_range_test_script""$objfile -s 8
    errecho "End Py evaluations"
    cd "$pwd"
}

function main(){
    update_properties_file
    run_evaluations
}


# Begin
main
