#!/bin/bash
#
# -- Run as: ./run_target_range_test_evenness_scaling.sh 1> test_output/stdout.txt 2> test_output/stderr.txt
#
errecho(){ >&2 echo $@; }

# Declare test ranges:
declare -a range_targets=("../models/ico_sphere/ico_sphere.obj" "../models/dome/dome_c.obj" "../models/dome/ico_2.obj")  #("1.25") #$(seq 3 90)  #e.g. ("44" "45")

# Declare test output location:
result_set="test_output/Target_Results_RangeTest_"$(date -d "today" +"%Y-%m-%d_%H")"-00"
relative_result_path_from_run="exp/Evenness_Scaling/"

# Specify properties file location(s).
default_properties_filename="../../properties/default.properties"
pre_default_properties_filename=$default_properties_filename".pre-"${result_set//\//-}
post_default_properties_filename=$default_properties_filename".post-"${result_set//\//-}



function pre_test_file_organisation(){
    # Prep File Organisation & properties file backup:
    mkdir -p $result_set
    cp -n $default_properties_filename $pre_default_properties_filename
}

function post_test_file_organisation(){
    # Backup the finished properties file into $post_default_properties_filename. (ensure there's a backup)
    cp -b $default_properties_filename $post_default_properties_filename
    # Restore the original properties file: (force)
    cp -f $pre_default_properties_filename $default_properties_filename
}

function update_properties_file_output_directory(){
    # Update the run.py evaluation results directory, by modifying the default.properties file:
    python helpers/update_default-properties_file.py "DO_OVERWRITE" $default_properties_filename "results_file.results_output_file_path_prefix=" "$relative_result_path_from_run""$result_set""/"
}

function run_range_test(){
    for n in "${range_targets[@]}"
    do
        ./run_target_evenness_scaling_trial.sh $n
        if [ $? -ne 0 ]; then
            errecho ""; errecho " -------------- "
            errecho "run_target_evenness_scaling_trial.sh failed."
            errecho "Exiting."
            exit 1;
        fi
    done
}

function main(){
    pre_test_file_organisation
    update_properties_file_output_directory
    run_range_test
    post_test_file_organisation
}

main
