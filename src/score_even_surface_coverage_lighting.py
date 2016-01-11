from __future__ import division
import operator, copy, random, sys

TESTING_DEBUG = False
IGNORE_TRI_LIGHTING_ERROR = True
IGNORE_LED_LIGHTING_ERROR = False
QUANTITY_OF_LEDS_REQUIRED = 1
MAX_DEPTH = 2
MAX_STEPS = 10
NUMBER_OF_TRIANGLES = None




# -----------------------------------------------------------
# -----------------------------------------------------------
# --------             Public Functions                 -----
# -----------------------------------------------------------
# -----------------------------------------------------------
def get_led_configuration_with_best_coverage( map_of_leds_to_triangles, number_of_triangles, 
                                              max_depth=MAX_DEPTH,
                                              max_steps=MAX_STEPS, 
                                              max_quantity_of_leds_required=QUANTITY_OF_LEDS_REQUIRED,
                                              ignore_tri_lighting_error=IGNORE_TRI_LIGHTING_ERROR,
                                              ignore_led_lighting_error=IGNORE_LED_LIGHTING_ERROR
                                              ):
    """ Return the error score (int) and a map of the best selected leds (dict) and a map of the best selected leds (dict).
         
    map_of_leds_to_triangles,       Dict: A dict of LED numbers as key. Each value contains an inner dict. (required)
                                          The inner dict key is a triangle number. The inner dict value is its 'reflection score' or heuristic value **.
    number_of_triangles,            Int:  The number of triangle of the target shape to light. (required)
    max_quantity_of_leds_required,  Int:  The quantity of best LEDs wanted in return set. (required)
    max_depth,                      Int:  The depth the stochastic search will attempt (default = 2). The depth will directly affect the search duration.
    max_steps,                      Int:  The number of stochastic selection attempts at each depth (default = 10). The steps will directly affect search duration.
    ignore_tri_lighting_error       Bool: If True, ignore when a triangle surface is never lit (default = True).
    ignore_led_lighting_error       Bool: If True, ignore when an LED never lights any triangle surfaces (default = False).
    
    ** The expected 'reflection score' value is a measure for the given LED, hitting the triangle surface.
       At time of writing, it is expected that the reflection score is calculated using an accumulation of the angle distance 
       from the LED-to-triangle-to-specular-reflection to the LED-to-triangle-to-cameras.
       
       In actual fact, any heuristic value would work here. The heuristic value is used in the following way:
       new_heuristic_value = 'Mean angle of the LED to each of its Tris' / (number of Tris Hit * number of Tris Hit)
    
    Selection of the "best selected leds", is the first selected LEDs with the lowest error score; on tie, the first is selected, 
    as sorted by only the score. Thus the first evaluated of the lowest error scoring sets can be expect to be chosen.
    """
    global NUMBER_OF_TRIANGLES, QUANTITY_OF_LEDS_REQUIRED, MAX_DEPTH, MAX_STEPS, IGNORE_TRI_LIGHTING_ERROR, IGNORE_LED_LIGHTING_ERROR
    NUMBER_OF_TRIANGLES         = number_of_triangles
    MAX_DEPTH                   = max_depth 
    MAX_STEPS                   = max_steps
    QUANTITY_OF_LEDS_REQUIRED   = max_quantity_of_leds_required
    IGNORE_TRI_LIGHTING_ERROR   = ignore_tri_lighting_error
    IGNORE_LED_LIGHTING_ERROR   = ignore_led_lighting_error
    led_map                     = map_of_leds_to_triangles
    
    
    validate_LED_Map(led_map)
    tri_map = convertMap_to_Tri_centric( led_map )
    validate_Tri_Map(tri_map)
    scores = select_and_prune(led_map, tri_map)
    scores = sorted(scores, key=operator.itemgetter(0))
    best        = scores[0]
    best_score  = best[0]
    best_config = best[1]
    best_leds   = convert_TriMap_to_SelectedLEDs( best_config )
    return best_score, best_config, best_leds














# -----------------------------------------------------------
# -----------------------------------------------------------
# --------            Helper Functions                  -----
# -----------------------------------------------------------
# -----------------------------------------------------------

def get_tri_indexes():
    global NUMBER_OF_TRIANGLES
    return xrange(NUMBER_OF_TRIANGLES)


def convertMap_to_Tri_centric(led_map):
    tris = get_tri_indexes()
    tri_map = {}
    for t in tris:              # Add all the tris
        tri_map[t] = []
    for m in led_map:           # Add all the known LED hits to the tri map, accumulate hits per tri.
        for k in led_map[m]:
            tri_map[k].append(m)
    return tri_map


def validate_Tri_Map(tri_map):
    if not IGNORE_TRI_LIGHTING_ERROR:
        for k in tri_map:
            if len(tri_map[k]) == 0:
                raise ValueError("Error: Triangle: '"+str(k)+"' was not hit by any LEDs.")
    else:
        for k in tri_map:
            if len(tri_map[k]) == 0:
                print("Warning: Triangle: '"+str(k)+"' was not hit by any LEDs.")
def validate_LED_Map(led_map):
    if not IGNORE_LED_LIGHTING_ERROR:
        for k in led_map:
            if len(led_map[k]) == 0:
                raise ValueError("Error: LED: '"+str(k)+"' did not hit any surfaces.")
    else:
        for k in led_map:
            if len(led_map[k]) == 0:
                print("Warning: LED: '"+str(k)+"' did not hit any surfaces.")


def convert_TriMap_to_SelectedLEDs( best_led_config ):
    """ Returns a lookup dict of the selected LEDs.
    """
    d = {}
    for tri_num in best_led_config:
        for led_num in best_led_config[tri_num]:
            d[led_num] = True
    return d










# -----------------------------------------------------------
# -----------------------------------------------------------
# --------            Private Functions                 -----
# -----------------------------------------------------------
# -----------------------------------------------------------

def modified_score_per_led(led_map):
    """ Get the modified score per LED. Ignore (remove) LEDs that hit no surface.
       
       The reflection value is used in the following way:
       new_heuristic_score = Shading Score * Tris Hit
                NO LONGER IN USE --> new_heuristic_score = 'Mean angle of the LED to each of its Tris' / (number of Tris Hit * number of Tris Hit)
    """
    scores = {}
    for k in led_map:
        if len(led_map[k]) > 0:
            tris_hit            = len(led_map[k])
            total_shading_score = sum(led_map[k].values())
            scores[k]           = total_shading_score * tris_hit
    return scores

def get_essential( m ):
    """ Get the "essential" leds, along with the associated tri. 
        Format: 'ess[led] = tri'
        An essential LED is an LED that lights a triangle surface, where that LED is the only LED to light that triangle surface.
        i.e. without that LED, the given triangle will never be lit.
    """
    ess = {}
    for k in m:
        if len(m[k]) == 1:
            led = m[k][0]
            ess[led] = k        #ess[led] = tri
    return ess

def get_empty_evaluation_dict():
    """ Get a dict of keys for all tris; each with an empty list for LEDs for each tri. 
        
        For example: 
            { tri0: [led0], tri1: [], tri2: [led0] } 
            where,  tri0 is only lit by led0. 
                    tri1 and tri2 are lit by several LEDs. 
                    tri1 is not associated with an essential LED.
                    However, tri2 is also lit by led0. As led0 is already selected, it will be guaranteed to hit tri2 and tri0.
                    We can also have multiple LEDs per tri (not shown in example). 
    """
    tris = get_tri_indexes()
    r = {}
    for t in tris:              # Add all the tris
        r[t] = []               # format:  r['tri_num'] = [list of led nums]
    return r
    
    
def rank_essentials( led_map, ess ):
    """ Get the best 'n' LEDs in the dict.
        Return 
    """
    #tri_dict   = {0: [0, 1], 1: [], 2: [], 3: [1], 4: [], 5: [0]}
    #led_map    = {0: {0: 43, 5: 89}, 1: {0: 33, 3: 50}, 2: {1: 20}, 3: {1: 70, 4: 30}, 4: {2: 60, 4: 30}, 5: {2: 75}, 6: {}}
    r = {}
    for led in ess:
        r[led] = len(led_map[ led ])
    return sorted(r.items(), key=operator.itemgetter(1))


def rank_desirables( led_map, ess ):
    score_map        = modified_score_per_led( led_map )
    score_map2       = copy.deepcopy(score_map)
    for e in ess:
        del(score_map2[e])
    ranked = sorted(score_map2.items(), key=operator.itemgetter(1))
    return ranked


def __add_to_dict_list( led, led_map, r ):
    """ Add an LED and its associated tris to the 'r' (dict[k]:[list]); return 'r'.
    """
    led_tris = led_map[led]
    for t in led_tris:
        r[t].append( led )
    return r
    
def __iterate_sorted_to_add_to_dict_list(ranked_list, running_limit, led_map, result):
    for tmp_led in ranked_list:
        led         = tmp_led[0]       # get led num
        score       = tmp_led[1]       # get score
        if running_limit == 0:
            break
        if running_limit > 0:
            running_limit -= 1
            result = __add_to_dict_list( led, led_map, result )
    return running_limit, result
    
#def select_essential_desired( sorted_desirables, led_map, sorted_essentials, limit, result ):
#    """ Populate the 'result' dict structure without exceeding the 'limit' number of entries. Keys are triangles. Values are a list of leds. Format: {[tri]: [led,led,..],..}
#        First add the ranked essential elements. Second add the ranked desirable elements. Never exceed the 'limit'.
#        If 'limit' is 0, return the unchanged result.
#    """
#    running_limit = limit
#    if running_limit > 0:
#        # Add essentials, up to limit:
#        running_limit, result = __iterate_sorted_to_add_to_dict_list( sorted_essentials, running_limit, led_map, result)

#    if running_limit > 0:
#        # Add desirabled ranked, up to limit:
#        running_limit, result = __iterate_sorted_to_add_to_dict_list( sorted_desirables, running_limit, led_map, result)
#    
#    return result


def select_essential_desired( sorted_desirables, led_map, sorted_essentials, limit, result, depth ):
    """ Populate the 'result' dict structure without exceeding the 'limit' number of entries. Keys are triangles. Values are a list of leds. Format: {[tri]: [led,led,..],..}
        First add the ranked essential elements. Second add the ranked desirable elements. Never exceed the 'limit'.
        Third, if depth > 0, then stochastically select 'depth' elements from the "remaining" ranked desirable elements. 
        "Remaining" are those that were not selected during First and Second stages.
        If 'limit' is 0, return the unchanged result.
    """
    
    running_limit = limit-depth
    if running_limit > 0:
        # Add essentials, up to limit:
        running_limit, result = __iterate_sorted_to_add_to_dict_list( sorted_essentials, running_limit, led_map, result)
    
    expected_top_desirables = running_limit
    if running_limit > 0:
        # Add desirabled ranked, up to limit:
        running_limit, result = __iterate_sorted_to_add_to_dict_list( sorted_desirables, running_limit, led_map, result)
    
    if depth > 0:
        has_desirable_leds_yet_to_be_selected = expected_top_desirables < len(sorted_desirables)
        if not has_desirable_leds_yet_to_be_selected:
            raise ValueError("All of the desirables were already selected, because there were so few.")
        else:
            # Add 'depth' LEDs to the result, randomly selected from the unselected desirables.
            remaining_sorted_desirables     = sorted_desirables[expected_top_desirables:]
            end_index                       = len(remaining_sorted_desirables)-1
            for i in range(depth):
                ind         = random.randint(0, end_index)              # Get the randomised LED for the result.
                tmp_led     = remaining_sorted_desirables[ind]
                led         = tmp_led[0]       # get led num
                score       = tmp_led[1]       # get score
                result      = __add_to_dict_list( led, led_map, result )
    
    if TESTING_DEBUG: print("led_map",led_map)
    if TESTING_DEBUG: print("result",result)
    if TESTING_DEBUG: print("score", get_surface_hit_score( result ))
    if TESTING_DEBUG: raw_input("wait")
    return result

def get_surface_hit_score( ess_desired_map ):
    """ Return an error score.
        - An error score of 0 , means all tris are lit by the selected LEDs.
    """
    err = 0
    for k in ess_desired_map:
        if len(ess_desired_map[k]) == 0:
            err += 1
    return err





def select_and_prune(led_map, tri_map):
    """ Using the led map and tri map, 
        Returns a list of lists. Inner list contains two elements: the (float) 'error score' and the (dict) 'hashed led configurations'.
        Format: [i][(float)'score', (dict)'hash containing the led configuration']
        
        An error score of 0 , means all tris are lit by the selected leds.
        A returned []  (empty list), means the quantity of LEDs required was zero; not allowed.
    """
    result_scores              = []    # [i][(float)'score', (dict)'hash containing the led configuration']
    
    if QUANTITY_OF_LEDS_REQUIRED <= 0:
        return result_scores
        
    ess             = get_essential( tri_map )
    desired_qty     = QUANTITY_OF_LEDS_REQUIRED
    empty_eval_dict = get_empty_evaluation_dict()
    sorted_essentials   = rank_essentials( led_map, ess )
    sorted_desirables   = rank_desirables( led_map, ess )
    
    # First Set: (top ranked)
    depth_change            = 0
    ess_desired_map         = select_essential_desired( sorted_desirables, led_map, sorted_essentials, desired_qty , copy.deepcopy( empty_eval_dict ) , depth_change )
    score                   = get_surface_hit_score( ess_desired_map )
    result_scores.append([score, ess_desired_map])
    
    # Subsequent Sets:
    step = 1
    depth_change = 1
    while (step < MAX_STEPS and depth_change <= MAX_DEPTH and depth_change <= desired_qty) and score != 0:
        try:
            ess_desired_map         = select_essential_desired( sorted_desirables, led_map, sorted_essentials, desired_qty , copy.deepcopy( empty_eval_dict ) , depth_change )
        except ValueError as excep:
            print(excep)
            depth_change +=1
            step = 1
            continue
        if TESTING_DEBUG: print("step,depth_change,desired_qty",step,depth_change,desired_qty)
    
        score               = get_surface_hit_score( ess_desired_map )
        result_scores.append([score, ess_desired_map])
        
        step+=1
        if step == MAX_STEPS and desired_qty < depth_change:
            depth_change +=1
            step = 1
    return result_scores





























# -----------------------------------------------------------
# -----------------------------------------------------------
# --------             Test code follows                -----
# -----------------------------------------------------------
# -----------------------------------------------------------



def getLEDMap():
    """ Notice that LED 6 does not hit any surface.
        Notice that Tri 5 is hit by LED 0.
    """
    return {0: {0: 43, 5: 89},
     1: {0: 33, 3: 50},
     2: {1: 20},
     3: {1: 70, 4: 30},
     4: {2: 60, 4: 30},
     5: {2: 75},
     6: {}}

def getLEDMap2():
    """ Notice that LED 6 does not hit any surface.
        Notice that Tri 5 is not hit by any LED.
    """
    return {0: {0: 43},
     1: {0: 33, 3: 50},
     2: {1: 20},
     3: {1: 70, 4: 30},
     4: {2: 60, 4: 30},
     5: {2: 75},
     6: {}}     

def test():
    global QUANTITY_OF_LEDS_REQUIRED
    led_map = getLEDMap()
    actual = False
    expected = True
    try:
        validate_LED_Map(led_map)
    except ValueError:
        actual = True
    if expected == actual: print("Pass","LED not hit any surfaces.") 
    if expected != actual: print("Fail","LED not hit any surfaces.") 

def test_required_leds( led_map, required=None, expected_error=None):
    global QUANTITY_OF_LEDS_REQUIRED
    global NUMBER_OF_TRIANGLES
    NUMBER_OF_TRIANGLES = 6
    QUANTITY_OF_LEDS_REQUIRED = required
    actual   = False
    config   = None
    expected = expected_error
    tri_map  = convertMap_to_Tri_centric( led_map )
    scores   = select_and_prune(led_map, tri_map)
    
    # Requires a valid set of LEDs to be selected
    if required > 0:
        scores = sorted(scores, key=operator.itemgetter(0))
        best    = scores[0]
        actual  = best[0]
        config  = best[1]
        if expected == actual: print("Pass","Total LEDs Required:",QUANTITY_OF_LEDS_REQUIRED,"Actual error score:",actual,"Expected",expected) 
        if expected != actual: print("Fail","Total LEDs Required:",QUANTITY_OF_LEDS_REQUIRED,"Actual error score:",actual,"Expected",expected)
        if expected != actual: print("----","Selected:",config)
        if expected != actual: print("----","led_map:",led_map)
    
    # Requires zero LEDs selected
    else:
        actual = scores
        if expected == actual: print("Pass","Total LEDs Required:",QUANTITY_OF_LEDS_REQUIRED,"Actual scores returned:",actual,"Expected",expected) 
        if len(scores) > 0:
            best    = scores[0]
            a_score = best[0]
            config  = best[1]
            if expected != actual: print("Fail","Total LEDs Required:",QUANTITY_OF_LEDS_REQUIRED,"Actual scores returned:",actual,"Expected",expected)
            if expected != actual: print("----","Selected:",config)





def test_runner():
    global TESTING_DEBUG
    TESTING_DEBUG = False
    test()
    led_map = getLEDMap()
    test_required_leds( led_map, required=0, expected_error=[])
    test_required_leds( led_map, required=1, expected_error=4)
    test_required_leds( led_map, required=2, expected_error=2)
    test_required_leds( led_map, required=3, expected_error=1)
    test_required_leds( led_map, required=4, expected_error=0)
    test_required_leds( led_map, required=5, expected_error=0)
    test_required_leds( led_map, required=6, expected_error=0)
    test_required_leds( led_map, required=7, expected_error=0)
    test_required_leds( led_map, required=8, expected_error=0)
    print "-------- New LED map (with unlit triangle 5) ------"
    led_map = getLEDMap2()
    test_required_leds( led_map, required=0, expected_error=[])
    test_required_leds( led_map, required=1, expected_error=4)
    test_required_leds( led_map, required=2, expected_error=2)
    test_required_leds( led_map, required=3, expected_error=1)
    test_required_leds( led_map, required=4, expected_error=1)
    test_required_leds( led_map, required=5, expected_error=1)
    test_required_leds( led_map, required=6, expected_error=1)
    print "--------"



def USAGE_EXAMPLE():
    led_map             = getLEDMap()
    number_of_triangles = 6
    print led_map
    print get_led_configuration_with_best_coverage( led_map, number_of_triangles, 
                                              max_quantity_of_leds_required=3, 
                                              max_depth=2,
                                              max_steps=10, 
                                              ignore_tri_lighting_error=True, 
                                              ignore_led_lighting_error=True )
    

if __name__ == "__main__":
    #test_runner()
    USAGE_EXAMPLE()






