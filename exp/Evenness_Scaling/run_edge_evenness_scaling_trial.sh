#!/bin/bash
errecho(){ >&2 echo $@; }

# ---------------------------------------------------------------------------------------
# Run example as:
#           -- ./run_edge_evenness_scaling_trial.sh 2 356
# ---------------------------------------------------------------------------------------

# Script Input arguments and defaults as globals:
if [ $# -ne 2 ]; then
    errecho "1 arguments required." 
    errecho "e.g.    ./run_evenness_scaling_trial.sh 2 356"
    errecho "Exiting."
    exit 1
fi


# Input arguments:
edge_value=${1:-"2"}    # EdgeX quantity
num_leds=${2:-"356"}    # Num of LEDs -> with support access on ico 3v = (265*(x-1))+91

timestamp=$(date -d "today" +"%Y-%m-%d_%H-%M")
path_to_run_evaluator="../../src/"

# Update the Properties File
function update_properties_file(){
    path_to_properties="../../properties/default.properties"
    errecho "Begin properties file update"
    python helpers/update_default-properties_file.py "DO_OVERWRITE" $path_to_properties "frame.number_of_vertices_per_edge=" $edge_value
    python helpers/update_default-properties_file.py "DO_OVERWRITE" $path_to_properties "results_file.number_of_leds=" $num_leds
    errecho "End properties file update"
}

# Run the Evaluations:
function run_evaluations(){
    pwd=""$(pwd)""
    cd "$path_to_run_evaluator"
    errecho "Begin Py evaluations"
    python run.py -p "../models/ico_sphere/ico_sphere.obj" -m2 -e4
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
