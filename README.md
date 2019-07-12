# AU LightStage Experimentation Framework

## Computer Science, Aberystwyth University, Wales, UK


# Key Features:

**Displays, evaluates and tunes LED light positions and intensities for a simulated object inside a Light Stage geodesic dome.** 



The key feature of the tool is an **Experimentation Framework** to evaluate different lighting and capture configurations for their effects on data capture in `3d-reconstruction` pipelines via `photometry`, `photometric stereo`, `structure from motion`, `photogrammetry` and other `single-viewpoint` and `multi-viewpoint` capture approaches.

Take a read below for details of those features, and how to use them. 

Feel free to check out the YouTube videos including [this one](https://www.youtube.com/watch?v=ESvpB2qFDgc&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=1) showing different Light Stage frames under the simulation: 

[![Video: LightStage Simulation](https://buildalightstage.files.wordpress.com/2019/05/myimage.gif)](https://www.youtube.com/watch?v=ESvpB2qFDgc&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=1)

# INSTALLATION & PREREQUISITES
    Python2.7.x (**Python 3 compatibility migration underway**).
    PyOpenGL
    numpy
    scipy
    Docker (for hardware in loop feature)
    

Downloading the [Anaconda distribution](https://www.anaconda.com/distribution/) should be sufficient, except for `Python wrapper for OpenGL`. The following methods have been successful for earlier users:

To install PyOpenGL on Windows:

        Download:       PyOpenGL version '3.1.1b1-cp27' as x64 or x86 from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl
        Install:        pip install path/to/download/PyOpenGL-3.1.1b1-cp27-none-win_XXXXX.whls

To install PyOpenGL on Linux (Ubuntu/ Debian):

        sudo apt install git python2.7 python-opengl python-pip
        sudo pip install -r requirements.txt

Clone the repo:

        git clone https://github.com/LightStage-Aber/LightStage-Repo.git
        cd src/

See `Usage Examples` below and take a read of `options switches` and `configuration file`, to make use of the full framework.


# BASIC MODES OF USE:
    python run.py -h.
        Displays options on command line.

    ./properties/default.properties (config file)
        Contains a number of comfigurations for the application, evaluations, tuning and display modes.

    python run.py -m1 -e3
        Display mode with LightIndexPositions mode, see the visualiation of the configured setup. Effected by ./properties/default.properties file, and command line options switches.
        Use default low-res target sphere (180 faces), default camera layout and LEDs defined with properties file.

    python run.py -m2 -e3
        Evalation mode

    python run.py -m3 -e3
        Tuning mode

        

# Experiment Framework:  `(-m2)`

Simply put, the tool is to evaluate light positions or search for positions that are optimised for data capture for 3d reconstruction. 
* Current evaluations measure physical effects of light. 
* Future evaluations may evaluate effects of positions in calibrated photometry.

A typical experiment might use a spherical lightstage frame on which lights are positioned to illuminate a typically spherical target object. The light received (illuminance) on each surface of the target object is calculated. The balance (i.e. a relative or normalised standard deviation) of the light received across the target, provides a measure of evaluation; this key metric, we call `evenness`. Other statistical measures are also reported. Variations include differently structured frames, different targets, light positions, quantities and light power output levels.

#### The state-of-art lightstages already simulated and evaluated include [Debevec's LS3/LS5 at USC, US](https://pdfs.semanticscholar.org/01ec/1c832e5af0c108c6c86f0eeb9f3958bbdb64.pdf) 156 LED icosahedron 2v, [Dutta & Smith in 2010 at UoYork, UK](http://etheses.whiterose.ac.uk/id/eprint/1498) 41 LED icosahedron 2v, and [Kampouris & Ghosh at ICL, UK](https://wp.doc.ic.ac.uk/rgi/project/multispectral-light-stage/) 168 sphere of rings design and [our stage at Aber Uni, UK](http://www.hannahdee.eu/blog/?p=1503) which is uses a icosahedron 3v structure. 

#### Here's a [video demonstrating Dutta, Debevec and Ghosh's](https://www.youtube.com/watch?v=ESvpB2qFDgc&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=2&t=0s)  (left-to-right) designs.

[![Video: LightStage Simulation](https://pmdscully.files.wordpress.com/2019/06/dutdebghosh_vid.png)](https://www.youtube.com/watch?v=ESvpB2qFDgc&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=1)


## Experiment Categories

Recently `illuminance-based` experiments have taken priority over `luminance-based` experimentation, as this removes camera positions and surface materials (BRDFs) from the evaluations. Luminance-based approaches do permit measuring (simulated) photometry data to evaluate different set-ups, etc. so they stil exist, but are under *re-enable at your own risk* status.

Prior experiments have evaluated different approaches and their results remain in `/results/`. These results are mostly from searches that outputed results suitable for input as `[LightIndexPositions]` (*described under Illuminance-based section*). They can be visualised/loaded using `-m1` and their corresponding `options switches` and `configuration file`. These include evaluating the light reflected into a set of cameras (single view or multi-view).

## Illuminance-based

For the illuminance tooling, light positions are defined (in `/properties/default.properties` configuration file) through two methods: 
1) vertex index number of the frame (`[LightIndexPositions], -e3/4`) and 
2) directly by the vertex coordinates (x,y,z) (`[LightPositions], -e7/8/9`). 

These modes are supported and available for Illuminance evaluations (e.g. `-m1/2/3 -e3/4/7/8/9`). 

For illumance evaluation, light received (illuminance) on the target object surfaces is calculated by the angle of incidence into the Lambertian (diffuse) distribution function. This differs from the luminance-based approach in that it measures absorption, rather than reflectance to a capture point.

## Luminance-based

Luminance-based evaluations are not currently supported. They were measured by bidirectional reflectance distribution functions (BRDF) such as Blinn-Phong (specular and diffuse) and Lambertian (diffuse only) reflectance models.

Search heuristics to guide luminance-based positioning have been disabled in favour of unguided illuminance evalutions. (**) 

These included `individual-based` and `set-based` heuristics:
1. selecting *individual* LEDs that maximised the lumens value received at the cameras (`maximised intensity`), and 
2. selecting LEDs that *individually* maximised lumens to the cameras, and also, as a *set* of LEDs, hit all (`coverage`) surfaces of the target object.

** Developers wanting to reinstate this approach should follow the `run.py -m2 -e0` call graph to test and re-establish, and see `/modes/luminance/luminance.py`.

### Example of Luminance-based results:

[![Video: LightStage Simulation with Wheat Plant Model](https://pmdscully.files.wordpress.com/2016/01/wheat1_intensity_score_663.png)](https://www.youtube.com/watch?v=Jdfgg7R9Vds&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=5)

Historically, the luminance-based option switches used `-m2 -e1` and `-m2 -e2` to evaluate `maximised intensity` and `coverage` scores, as shown in the video above.

Run the `maximised intensity` configuration demo, shown in the video above, as:

    python run.py -m1 -p "../models/wheat/wheat1.obj" -s 1 -t '(0,-0.1,0)' -r '../results/blinn-phong+lambert_shading_scores/wheat1_realistic_cam/led_scores_2016-01-12-17-11-28.csv'


## Experiment Outputs

Key experiment statistical metrics are printed to STDOUT. 

All experiment data is recorded to a CSV file (filename specified in STDOUT) and written to the directory specifed in `results_file.results_output_file_path_prefix=` or `light.results_output_file_path_prefix=` in the `./properties/default.properties` configuration file. Default is a subdirectory of `./results/`.

The output filename corresponds to the experiment type (for example, `*_VertexIndexPositionEvaluator.csv`, corresponds to `-e3` experiments (Joint or "Vertex" Positions from Index).

Below is a list of the CSV column header titles (correct at time of writing):

    [Qty_Selected_LED_Indexes, Qty_Available_LED_Indexes, total_surface_lambertian_score, normalised_stdev_n, normalised_stdev_n_intensity, MEAN_INTENSITY, UNIFORM_LED_INTENSITIES, coefficient_of_stdev, coefficient_of_iqr_median, surface_mean_score, surface_stdev, surface_median, surface_iqrange, surface_min, surface_max, Evaluator_Shortname, source_filename, Evaluator_ClassName, frame_objfilename, frame_scale, obj.TARGET_SHAPE, obj.TARGET_SCALE, obj.TARGET_TRANSLATION, surfaces_raw_data, timestamp, light_indexes, light_vertices, light_intensities] 

Details of the output data format are specified in the functions of `./src/modes/illuminance/helper_illuminance.py`. 


## Details of Experiment Configurations

The different types of configuration variations can be configured and executed as follows:

### Target Object: 
See `run.py` options switches.

    - specify target (.obj)         -p '/path/to/tri-surface-WaveFront-Object-file.obj'
    - adjust target scale           -s scale (relative to frame, default is 1)
    - adjust target position        -t translate position
        
### Frame:
See configuration under `default.properties [FrameModel]` section.

    - specify target (.obj)                 frame.objfilename=path/to/Poly-Face-WaveFront-Object-file.obj
    - adjust frame scale                    frame.scale (relative to target object, default is 8)
    - remove lower mount points             frame.withsupportaccess=True
    - specify n mount points to remove      frame.support_access_vertices_to_remove=1 (remove 1 bottom-most y-axis vertex from frame)
    - specify frame EdgeN mounting points   frame.number_of_vertices_per_edge=1, Edge1, Edge2,.. Edge10.
    

### Lights by Vertex Positions:
See configuration under `default.properties [LightPositions]` section.

    - specify light positions from file     light.objfilename=path/to/Poly-Face-WaveFront-Object-file.obj - This specifies quantity and vertex positions, in WaveFront OBJ format.
    - specify results output file prefix    light.results_output_file_path_prefix=/path/
    - adjust vertex position scale          light.scale= (relative to target object, should correspond to frame.scale, default is 8) Usage includes Euclidean k-nearest neighbour mapping of floating light vertex positions to frame vertex positions.

### Lights by Frame Index Positions: 
See configuration under `default.properties [LightIndexPositions]` section.

    - specify light index positions from file       results_file.csvfilename=path/to/filename.csv - This contains a binary column (0/1). Row number corresponds to vertex index number from the frame's OBJ file.
    - specify the column binary number              results_file.column_number= (historical default from the luminance-based results files is, 3)
    - specify quantity of LEDs to load and display  results_file.number_of_leds= (read in n rows with value '1', a count ignoring '0's).
    - specify results output file prefix            results_file.results_output_file_path_prefix=/path/


### Light Intensity Configuration (Output per Indexed Light): 
See configuration under `default.properties [LightOutput]` section.

This section of configuration let's us define a set of light intensities, either by (1) an `enforced_default` or by (2) a `column_number` specified within a CSV file defined by `filename_path`. The baseline value is 1.0.

    light.output_intensity_from_index.enforce_default=True
    light.output_intensity_from_index.default_value=1.0
    light.output_intensity_from_index.allow_default=False
    light.output_intensity_from_index.column_number=4
    light.output_intensity_from_index.filename_path=../results/Control_91-92_March2017/edges_l3926.csv

* **Non-uniform light intensities** can improve target lighting balance, see the **Brightness Control Tuning** section for the automated improvement procedure.

* **Uniform light intensities** have no effect on balance peformance.

* The `Readme First` recommendation is to modify and compare only between variations of a single dependent variable (e.g. positions or intensities or target or frame, but not multiple). Drawing statistical comparisons, while modifying the position sets and these intensity values, can be unreliable.

* Further explanation of these configuration options and their statistical analysis are released on the accompanying website.



# Experiment Configurations to Mount LED Lights to Frame Edges

In real world Light Stages, the LED lights can be mounted anywhere on the frame. The `frame.number_of_vertices_per_edge` parameter in the `default.properties` config file defines the number of discrete mounting points along each frame edge.

`Edge2` is used by setting the value to `2`. This will add an extra central point along each edge, such that the vertex mount points include joints and 1 point on each edge. For `Edge2,.. to Edge10`, the quantity of mount points is equal to `(|E|*(x-1))+|V|`, where `|V|` is the quantity of joints and `|E|` is the quantity of edges.

`Edge1` is a special case, used by setting the value to `1`. This will add a central point along each edge; however, no joints will remain available. `Edge1` delivers a quantity of mount points equal to `|E|`. 

[This video](https://www.youtube.com/watch?v=ESvpB2qFDgc&list=PLDt0joxz3D16g-DcYcdirf05QcMTTpTiz&index=1) shows examples of `Edge1` and `Edge2` features. On right, Ghosh's design uses `Edge1`. In the middle, Debevec's LS3/5 design uses `Edge2`. On left, Dutta's design does not use edge mounting.

Edge 1 | Edge 2| Edge 4
------|------|------
![Edge 1 Example](https://buildalightstage.files.wordpress.com/2019/06/edge1.png) | ![Edge 2 Example](https://buildalightstage.files.wordpress.com/2019/06/edge2.png) | ![Edge 4 Example](https://buildalightstage.files.wordpress.com/2019/06/edge4.png)


# Display Experiment Environment `(-m1)`

The tool will visually display the experiment configuration (without running the evaluation). This helps with: 

1. visual verification of an experiment set-up.
2. demonstrations of experiment set-ups.

Together with the associated **configuration file** and **options switches**, run with:

    python run.py  -m1   -e<3,4,7,8,9>

Switch back to experiment mode with:


    python run.py  -m2   -e<3,4,7,8,9>

Display example showing an Edge 3 dome visualisation  |
-------------------|
* Created an with `Edge 3` configuration set-up in `properties/default.properties` 
* Run as `python run.py -m1 -e4`


<img src="https://buildalightstage.files.wordpress.com/2019/05/myimage-1.gif" width="500" height="380">


# Optimise Evenness of any Light Position Set: `(-m3)`

Given a set of light positions, the illumination balance can often be improved by fine tuning the balance of intensity (lumens output or power) emitted by each LED light. In other words, this feature is to find a way to lower the standard deviation of the distribution (evaluation data) by effecting the inputs into the scoring function.

In the current release you can enable this feature with mode `-m3`. Two strategies to improve the `evenness` balance of a set of LEDs are provided.

### Optimisation Types:

1. `iterative regression` reduces the target object's surface illumination normalised standard deviation (`evenness` metric) by iteratively modifying the light output intensity value of the LED with an *illuminance score* furthest from the mean. This is done to lower the standard deviation of the target's surface illumination scores.
2. `scipy.optimize.basinhopping` uses the `L-BFGS-B` search method to optimise the `evenness` metric, by modifying the array of light intensity values within a bounded (min/max) range.

Both methods have a set of parameters to configure in `./properties/default.properties` under section `[BrightnessControlTuner]`. The optimisation search stopping criteria include iterations and thresholds. 

### How to Run:

The brightness control tuning can be applied to all forms of light positions sets (i.e. Index `-e3/4` and Vertex `-e7/8/9`). 

Within the **configuration file** and **options switches** the optimisation stopping criteria and frame lighting design conditions should be set-up. 

Then, run as:

    python run.py -m3 -e<3,4,7,8,9>

### Data Output:

* The key data output from the tuning is an array of new **light output intensities**. 

* These are light output values that correspond to the **ordered** (by vertex order or by index order, depending on the trial) light positions. 

* The intensity values can inform the power output per light in a physical light stage control system. It is advisable to scaling these values into a [0.0 to 1.0] range, then translate into physical light's control's power (i.e. wattage) range (e.g. [0 to 256]).

* The improved **light output intensities** set (`intensities` column) and corresponding LED index positions (column `led_indexes`) are written to a unique output file with identifying suffix information:

    * Filename format: `Results_Illuminance__Tuned__QtySet_QtyAvail_Evaluator_ClassName_CoVScore_timestamp.csv`.
    * This file path can be used directly as input to the `light.output_intensity_from_index.filename_path=` property. Set `column_number=1` and `skip_header=True`.


* The rest of the result statistics data (including the improved **light output intensities** set in the `light_intensities` column) is written to the `Results_Illuminance_*.csv` file.

#### Recommendations and Reading:

1. Recommend to start with `iterative regression`, which has been *beta* tested. For sub-optimal position sets, this algorithm can rapidly improve scores. For already optimised positions, this can perform poorly.

2. Read the algorithms (`./src/modes/brightness_control_tuning/`), documentations (e.g. scipy / pydocs) and configuration file settings for more details.

3. Read and run the unit tests and their configuration changes in `./test/test_BrightnessControl.py` with nose2 or by executing the py file.


# OTHER USEFUL DETAILS

### KEYBOARD/MOUSE CONTROLS:

    Press F1, see the console print outs.
    Use mouse to drag and zoom view of object.
    Use spacebar to stop/start display rotation.
    Press Esc to quit.
    


### FILE STRUCTURE:

    /src            - Code.
    /test           - Unit tests for src/ code.
    /models         - Sample 3D obj model files.
    /results        - Example result data files for various experiment types and example input .csv/.obj files.
    /properties     - Configuration file to simplify running of experiments, visualisations, etc. (-f 'path/file.properties')
    /exp            - Experiment scripts for batch and single trials. Includes charged particle repulsion positioning (Lettvin) and range testing for evaluating metrics.
    /vendor	    - Third party content, including docker container scripts and dependency support scripts.




### FORMER LUMINANCE-BASED EXAMPLES:
    
The (`-m1 -e0`) executes the code associated with luminance-based tools for evaluating and viewing lightstage models.

The (`-m1 -e0`) viewing code is still operable, such that first example below will display an LED position result set (defined in `-r`).

    python run.py -m1 -p "../models/Flower/plants3.obj" -s 0.01 -t '(0,-4,0)' -r '../results/blinn-phong+lambert_shading_scores/wheat1_realistic_cam/led_scores_2016-01-12-17-11-28.csv'
        
        Run in display mode, with plants3.obj target model loaded (-p), with a scaling factor (-s) of 0.01 and translated (-t) -4 on the Y-axis
        Loads result data file (-r) for the wheat1 model: ../blinn-phong+lambert_shading_scores/wheat1_realistic_cam/led_scores_2016-01-12-17-11-28.csv

`Please note:` the earlier luminance-based evaluation methods have been disabled in favour of illuminance-based evaluations. The code is still there, but needs testing. Follow the `run.py -m2 -e0` call graph to test and re-establish that evaluation tooling. 


    python run.py -m 2 

        Run in evaluation mode (-m), with default mini-dome, default camera layout (-c) and default required LEDs (-l).
        
        Creates information file: ../led_meta_data_YYYY-MM-DD-hh-mm-ss.txt
        Creates result data file: ../led_scores_YYYY-MM-DD-hh-mm-ss.csv



## Community

**Issues**: If you find any issues, please [file it](https://github.com/LightStage-Aber/LightStage-Repo/issues).

**Slack**: We're fairly responsive on [slack](https://join.slack.com/t/lightstage-uk/shared_invite/enQtNjg2MTQzNDU3MTUzLWYxMWFiYWY2MmY4MzFlODJlNTk4OGNmNzhiMmQ1MzY2MWU4ZmMxNWEzNGJkZDA1MWM1OTg1ZjMwNjg5MjEyNjY) and you can find us in the #lightstage channel.


