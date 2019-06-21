#!/bin/bash

# NOTE: this script is run on the expanded dataset, extracted via the "extract_lettvin_config_from_csv_results.py" script.

#path_to_results="Results_RangeTest_2017-06-11_09-00/"
path_to_results="Results_RangeTest_2017-06-06_14-00/"
path_to_output_plots="Latex_Plots/"

EXTRACT_LETTVIN_DATA=0
CREATE_PLOTS_LATEX_TABLES=1

if [[ $EXTRACT_LETTVIN_DATA -eq 1 ]];
then
    echo "extract"
    python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" $path_to_results"lambertian_led_sets_RawPositionEvaluator.csv" "outfile_RawPositionEvaluator.csv" "../../"
    python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" $path_to_results"lambertian_led_sets_VertexMappedPositionEvaluator.csv" "outfile_VertexMappedPositionEvaluator.csv" "../../"
    python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" $path_to_results"lambertian_led_sets_Edge10MappedPositionEvaluator.csv" "outfile_Edge10MappedPositionEvaluator.csv" "../../"
fi

if [[ $CREATE_PLOTS_LATEX_TABLES -eq 1 ]];
then
    echo "create"
    mkdir -p $path_to_output_plots
    python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "outfile_RawPositionEvaluator.csv" "results_table_RawPositionEvaluator.tex" "Raw Lettvin Positions" $path_to_output_plots
    python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "outfile_VertexMappedPositionEvaluator.csv" "results_table_VertexMappedPositionEvaluator.tex" "Mapped to dome vertices (92 points)" $path_to_output_plots
    python produce_Plots_Latex_Tables_for_Lettvin_Tests.py "DO_OVERWRITE" "outfile_Edge10MappedPositionEvaluator.csv" "results_table_Edge10MappedPositionEvaluator.tex" "Mapped to dome edges (10 points per edge. 3923 total points)" $path_to_output_plots
fi