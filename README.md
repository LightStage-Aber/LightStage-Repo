# LightStage V3 Project Code
#### Dept Computer Science, Aberystwyth University


#### WHAT DOES THIS PROGRAM DO?:

    (1) EVALUATES the illumination of a simulated object inside a LightStageV3.
    (2) DISPLAYS the resulting configuration(s) of LEDs that produce the best illumination of that object. 
    - These evaluations are based on two metrics that use the Lambertian diffuse and Blinn-Phong specular reflectance models.
    

#### DEMO VIDEO of LIGHTSTAGE SIMULATION
[![Video: LightStage Simulation with Wheat Plant Model](https://pmdscully.files.wordpress.com/2016/01/wheat1_intensity_score_663.png)](http://www.youtube.com/watch?v=Jdfgg7R9Vds)


#### PREREQUISITES
    Python2.7.x (5)
    PyOpenGL
    numpy
    
    To install PyOpenGL on Windows:
        First download:         PyOpenGL version '3.1.1b1-cp27' as x64 or x86 from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl
        Then install as:        pip install path/to/download/PyOpenGL-3.1.1b1-cp27-none-win_XXXXX.whl

    To install PyOpenGL on Linux (Ubuntu/ Debian):
        sudo apt-get install python2.7 python-opengl numpy

    
#### USAGE EXAMPLES:
    python run.py
        Run in display mode, with default mini-dome, default camera layout and default required LEDs.

    python run.py -p "../models/Flower/plants3.obj" -s 0.01 -t '(0,-4,0)' -r '../blinn-phong+lambert_shading_scores/wheat1_realistic_cam/led_scores_2016-01-12-17-11-28.csv'
        Run in display mode, with plants3.obj target model loaded (-p), with a scaling factor (-s) of 0.01 and translated (-t) -4 on the Y-axis
        Loads result data file (-r) for the wheat1 model: ../blinn-phong+lambert_shading_scores/wheat1_realistic_cam/led_scores_2016-01-12-17-11-28.csv

    python run.py -m 2 
        Run in evaluation mode (-m), with default mini-dome, default camera layout (-c) and default required LEDs (-l).
        This takes ~75 seconds to run.
        Creates information file: ../led_meta_data_YYYY-MM-DD-hh-mm-ss.txt
        Creates result data file: ../led_scores_YYYY-MM-DD-hh-mm-ss.csv

    python run.py -h
        Display options on command line.


#### KEYBOARD/MOUSE CONTROLS:

    Press F1, see the console print outs.
    Use 'mouse' to drag and zoom view of object.
    Use 'space' to stop/start display rotation.
    
