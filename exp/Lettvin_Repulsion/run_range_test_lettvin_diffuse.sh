#!/bin/bash

# Declare test ranges:
declare -a range_n=$(seq 3 2 90) #$(seq 3 90)  #e.g. ("44" "45")
declare -a range_j=("0.001" "0.0001" "0.00001" "0.000001" "0.0000001")
declare -a range_r=("0")
max_iterations=50

# Declare test output location:
result_set="test_output/Results_RangeTest_"$(date -d "today" +"%Y-%m-%d_%H")"-00"
relative_result_path_from_run="exp/Lettvin_Repulsion/"

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
    python helpers/update_output_directory_in_default-properties_file.py "DO_OVERWRITE" "$default_properties_filename" "$relative_result_path_from_run""$result_set""/"
}


function run_range_test(){
    for n in $range_n
    do
        for j in "${range_j[@]}"
        do
            for r in "${range_r[@]}"
            do
                for i in $(seq 1 $max_iterations)
                do
                    ./run_lettvin_diffuse_algorithm.sh "$n" "$j" "$r" "$i" "$result_set"
                done
            done
        done
    done
}

function main(){
    pre_test_file_organisation
    update_properties_file_output_directory
    run_range_test
    post_test_file_organisation
}

main