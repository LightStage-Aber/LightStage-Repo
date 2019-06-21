#!/bin/bash

# NOTE: this script is run on the expanded dataset, extracted via the "extract_lettvin_config_from_csv_results.py" script.

PATH="Results_RangeTest_2017-06-11_09-00/"

file1="lambertian_led_sets_RawPositionEvaluator.csv"
file2="lambertian_led_sets_VertexMappedPositionEvaluator.csv"
file3="lambertian_led_sets_Edge10MappedPositionEvaluator.csv"

outfile1="lettvin_outfile_RawPositionEvaluator.csv"
outfile2="lettvin_outfile_VertexMappedPositionEvaluator.csv"
outfile3="lettvin_outfile_Edge10MappedPositionEvaluator.csv"

python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "$PATH$file1" "$outfile1"
python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "$PATH$file2" "$outfile2"
python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "$PATH$file3" "$outfile3"
#python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "$PATH$file1" "results_table_lettvin_March19th2017.tex" "Raw Lettvin Positions"
#python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "output_March19th2017.csv" "results_table_vertices_lettvin_March19th2017.tex" "Mapped to dome vertices (91 points)"
#python extract_Lettvin_Parameter_Values_From_Filename_Per_Test.py "DO_OVERWRITE" "output_March19th2017.csv" "results_table_edges_lettvin_March19th2017.tex" "Mapped to dome edges (10 points per edge. 3926 total points)"
