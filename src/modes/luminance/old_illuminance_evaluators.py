
''' AOS TEST
# -----------------------------------------------------------
def evaluate_illuminance_score_result_file_set_tune_weights( updateable_line, camerasVertices, triangles, shape_name ):
    global cameraPos, scale, logged_score_to_file, loggable

    best_LEDs        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
    led_index_set    = get_sorted_column_from_result_file( best_LEDs, CSV_METRIC_COLUMN_INDEX=3, QTY_OF_BEST_LEDS_REQUIRED=44 )

    all_leds        = draw_dome( scale , True )

    print len(led_index_set)
    led_vertex_weights = np.ones(len(all_leds))

    faces = dome_obj_data.get_dome_faces()

    led_vertex_set = []
    for led_num in led_index_set:
        led_vertex_set.append( all_leds[led_num] )
    # aos test
    print 'RUNNING FULL LAMBERTIAN EVALS'
    multi_surfaces    =  get_full_set_surface_evaluations(triangles, all_leds)
    #print(multi_surfaces)

    # try to smooth the surface variations
    for i in range(1000):

      #sum the lambertian scores from each led that is selected
      lam_scores = np.zeros(len(triangles));
      for led_num in led_index_set:
	for t in range(len(triangles)):
	    lam_scores[t] += multi_surfaces[led_num,t] * led_vertex_weights[led_num]

      #get the mean value and find the face furthest from the mean
      mean = np.mean(lam_scores)
      worst_face=0
      worst_face_delta=0
      for t in range(len(triangles)):
        delta = np.absolute(lam_scores[t] - mean)
        if ( delta > worst_face_delta):
          worst_face_delta = delta
          worst_face = t

      # process the 3 vertices on the worst face
      delta = mean - lam_scores[worst_face]

      vertices = faces[worst_face]
      #for vertex in range (1,4):
	#print vertices[vertex] - 1
      #  led_vertex_weights[vertices[vertex] -1] += 0.01 * np.sign(delta)

      max = 0
      max_led=0
      for led_num in led_index_set:
        if(multi_surfaces[led_num,worst_face] > max):
          if(led_vertex_weights[led_num] > 0.6):
            max = multi_surfaces[led_num,worst_face]
            max_led = led_num

      led_vertex_weights[max_led] += 0.01* np.sign(delta)

      #print lam_scores
      print np.std(lam_scores)
      print np.mean(lam_scores)
      print worst_face_delta
      print worst_face
      # end aos test

    print led_vertex_weights
'''






# PDS7 REFACTORING
class MeasureIlluminanceTuneWeights_AOS(EvaluatorGeneric):
    def evaluate( self, updateable_line, camerasVertices, triangles, shape_name ):
        global cameraPos, scale, logged_score_to_file, loggable

        best_LEDs        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
        led_index_set    = get_sorted_column_from_result_file( best_LEDs, CSV_METRIC_COLUMN_INDEX=3, QTY_OF_BEST_LEDS_REQUIRED=44 )

        all_leds        = draw_dome( scale , True )

        print len(led_index_set)
        print led_index_set

        led_vertex_weights = np.zeros(len(all_leds))

        for led in led_index_set:
            # print led
            led_vertex_weights[led] = 1.0

        faces = dome_obj_data.get_dome_faces()

        led_vertex_set = []
        for led_num in led_index_set:
            led_vertex_set.append( all_leds[led_num] )
        # aos test
        print 'RUNNING LED WEIGHT EVALS'
        multi_surfaces    =  get_full_set_surface_evaluations(triangles, all_leds)
        # print(multi_surfaces)

        best_weighting = np.copy(led_vertex_weights)
        best_std_dev = 10000

        # try to smooth the surface variations
        for i in range(1000):

            # sum the lambertian scores from each led that is selected
            lam_scores = np.zeros(len(triangles));
            for led_num in led_index_set:
                for t in range(len(triangles)):
                    lam_scores[t] += multi_surfaces[led_num ,t] * led_vertex_weights[led_num]


            dev = np.std(lam_scores) if(dev < best_std_dev):
                best_std_dev = dev
                best_weighting = np.copy(led_vertex_weights)
            else:
                led_vertex_weights = np.copy(best_weighting)

            rand = rnd.randint(0,len(all_leds )/2)
            led_vertex_weights[rand] -=0.01
            led_vertex_weights[91 - rand] -=0.01

            # print lam_scores
            print np.std(lam_scores)
            #      print np.mean(lam_scores)
            # end aos test

        print best_weighting


'''
# -----------------------------------------------------------
def evaluate_illuminance_score_multiple_result_file_set( updateable_line, camerasVertices, triangles, shape_name , count, kwords):
    """
    Based on an initial set of LED positions.
    Randomly swap-in/out 1 from top-half and 1 from bottom-half of dome.
    Continue until the count is exceeded.
    Measure standard deviation of suface illuminance, whlie measuring lambertian score from current LED set.
    Report lowest standard deviation score and its LED index set.
    """
    global cameraPos, scale, logged_score_to_file, loggable



    best_LEDs        = file_io.read_in_csv_file_to_list_of_lists( kwords['LED_SCORE_LOG_FILE'], skip_header=False )
    led_index_set    = get_sorted_column_from_result_file( 	best_LEDs,
    														kwords['CSV_METRIC_COLUMN_INDEX'],
    														kwords['QTY_OF_BEST_LEDS_REQUIRED']
    														)



    # store the active leds
    selected_leds = np.zeros(len(kwords['all_leds']))
    for led_num in led_index_set:
        selected_leds[led_num] = 1

    multi_surfaces    =  get_full_set_surface_evaluations(triangles, kwords['all_leds'])

    best_stddev = 100

    for i in range(count):
        #sum the lambertian scores from each led that is selected
        num_tri = len(triangles);
        lam_scores = np.zeros(num_tri);
        for led_num in range (len(selected_leds)):
            if(selected_leds[led_num] == 1):
                for t in range(num_tri):
                    lam_scores[t] += multi_surfaces[led_num,t]

        stddev = np.std(lam_scores)
        if(stddev < best_stddev):
            best_stddev = stddev
            active_leds = []
            for led_num in range (len(selected_leds)):
                if(selected_leds[led_num] == 1):
		    active_leds.append(led_num)

            print str(stddev) + "for led set:"+str(active_leds) + '  (leds: ' + str(np.sum(selected_leds)) + ')'
        else:
            #print str(stddev) + "for led set:"+str(active_leds) + '  (leds: ' + str(np.sum(selected_leds)) + ')'
            if(i%100 == 0): print '(' + str(i) + ')' + str(stddev)

	#modify the led pattern
	#get random positions of active and inactive less, and toggle them (preserving total active count)
        #mirror the top and bottom halves to preserve symmetry

	active = rnd.randint(0,21)
	inactive = rnd.randint(1,22)

	jump_count = 0
	inact_index =0
	while (jump_count < inactive):
	    inact_index += 1
	    jump_count += 1 - selected_leds[inact_index]

	#print 'inact ' + str(inact_index) + ' (' + str(inactive) + ')'

 	jump_count = -1
	act_index =0
	while (jump_count < active):
	    act_index += 1
	    jump_count += selected_leds[act_index]

	#print 'act ' + str(act_index)

 	selected_leds[inact_index] = 1
 	selected_leds[91 - inact_index] = 1
 	selected_leds[act_index] = 0
 	selected_leds[91 - act_index] = 0

	#print sum(selected_leds)



'''


# -----------------------------------------------------------
def evaluate_illuminance_score(updateable_line, camerasVertices, triangles, shape_name ):"""
    Measure illuminance of surfaces.
    Create a set of randomly selected LED sets.
    Ignore LED sets that do not illiminate all sufaces of the spherical model.
    Report the total lambertian score, measured per LED per hit surface.
    Report the standard deviation of lambertian scores over the set of spherical model surfaces.
    """
    global cameraPos, scale, logged_score_to_file, loggable

    # BEST_LED_DATAq        = file_io.read_in_csv_file_to_list_of_lists(LED_SCORE_LOG_FILE, skip_header=False)
    # #best_LEDs   = get_best_leds_from_file()
    # print(BEST_LED_DATAq)
    # print(len(BEST_LED_DATAq))
    # best_LEDsq   = [x[0] for x in BEST_LED_DATAq if x[3] == '1']
    # print(best_LEDsq)
    # print(len(best_LEDsq))
    # sys.exit()

    string = []
    drawTextString = []
    l,r,d = 0,0,0 all_leds = draw_dome( scale , False )
    printsequence_size   = 44
    max_depth       = 1 led_sequence    = all_leds[ :91]  # [4,7,10,11,12,69,72,81,86,87,14,15,16,17,19,21,22,23,30,33,54,56,57,59,62,65,66,68,75,78,26,29,32,35,38,39,40,42,43,46,49,51,52,55,58,60,61,63,64,67,24,25,27,28,31,34,36,37,41,44,45,47,48,50,53,70,73,76,79,82,8,9,13,18,20,71,74,77,80,83,1,2,3,5,6,84,85,88,90,91,0,89];
    index_stop_search   =  1

    led_sets        = monte_carlo_sequences. get_led_sets_selected(all_leds, led_sequence, sequence_size, max_depth, index_stop_search)
                                                           candidate_led_sets = []
    led_sets_compute = 0
    progress = 0

    led_set = []
    for index in led_sequence[:44]:
        led_set.append(all_leds[index])
    print(stdev_selected_set(triangles, led_set))
    sys.exit()
    startTime = currentMillis()
    if not DO_EVALUATIONS:
        leds                = [updateable_line.get_point()]  # Use reflections from single light selected by arrow-keys.
        triangles           = TARGET_TRIANGLES[:10]
        shape_name          = "Test Tri" led_sets            = led_sets[0]
    else:
        file_io.write_to_csv(["led_set", "total_set_lambertian_score", "standard deviation"], "../",
                             "lambertian_led_sets_search.csv")
    # Note: One led hits 50% of surfaces.

    for leds in led_sets:  # For all sets of LED positions with set magnitude 42.
        surfaces    = get_surface_evaluations(triangles, leds)

        # print the progression of the total computes
        led_sets_compute+=1
        percent = int(led_sets_compute *100 / len(led_sets))
        if( percent > progress):
            progress = percent
            print 'Progress : {} %'.format(progress)

        if are_all_surfaces_hit(surfaces) == False:
            break
        else:
            # if yes we can have the total lambertian score and standard deviation for this set and write it in the csv file
            row = write_led_set_lambertian_scores_appended_result_file(all_leds, surfaces, leds)
            candidate_led_sets.append(row)


    print(str(len(

    candidate_led_sets)) + " sequences computes")
    candidate_led_sets = sorted(candidate_led_sets, key=lambda candidate_led_sets: candidate_led_sets[2])
    best_candidate_leds_index_set = candidate_led_sets[0][0]

    write_led_result_file(all_leds, best_candidate_leds_index_set)


'''

# calculate the target surface illumination for all led for all faces
def get_full_set_surface_evaluations(triangles, leds):
    surfaces = np.zeros((len(leds),len(triangles)))
    for led_num in range(0, len(leds)) :                    # For all of the leds:
        for tri_num in range(0,len(triangles)):
            tri = triangles[tri_num]
            make_triangle_face( tri )
            c  = find_center_of_triangle( tri )
            n1 = find_perpendicular_of_triangle( tri )              # Get normal of current tri plane.
            l, r    = reflect_no_rotate( c, leds[led_num], n1 )
            """ usage of l and r require a prior-translate to c.
            """
            if is_front_facing_reflection(tri, l, r):       #Also see: __debug_is_cullable_reflection(tri, OTri, l, r, c )
                draw_incident_ray(c, l)
                lamb_diffuse        = reflect_models.Lambert_diffuse( incident_vector=l, surface_norm=n1, intensity=1.0 )

                score               = lamb_diffuse  # Get Lambertian intensity value (x1) per surface per led. --> [surface] = accumulated score.
                surfaces[led_num][tri_num]   += score
    return surfaces



def stdev_selected_set(triangles, leds):

    surfaces    = get_surface_evaluations(triangles, leds)

    stdev_set = 0
    all_surfaces_hit = 1
    for score in surfaces:
        if (score == 0):
            all_surfaces_hit = 0
            break

    #if yes we can have the total lambertian score and standard deviation for this set and write it in the csv file
    if(all_surfaces_hit == 1):
        total_set_lambertian_score = np.sum(surfaces)
        stdev_set = np.std(surfaces)
    return stdev_set


'''

