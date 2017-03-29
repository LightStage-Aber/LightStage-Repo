from __future__ import division
import numpy as np


def get_sorted_column_from_result_file( best_led_data, column_index, qty ):
    """
    BEST_LED_DATA, CSV_METRIC_COLUMN_INDEX, QTY_OF_BEST_LEDS_REQUIRED
    """
    assert( type(best_led_data) is list )
    assert( column_index >= 0 )
    assert( qty >= 0 ) 
    # Order by column index. Take top values. Get index positions. Return list of 
    l = best_led_data
    l = sorted(l,key=lambda x: x[column_index], reverse=True)
    l = l[:qty]                         # Get top n positions
    l = np.array(l)[:,0]                # Get only index positions
    l = list(l)                         # Convert back to py list
    l = [int(x) for x in l]             # Convert strings to ints.
#    print l
    return l




def try_to_verify_symmetry( best_led_data, column_index=3 ):
    """
    Try to verify if the selected LEDs are paired with their corresponding (symmetric) LED positions...

    NOTE:   This is intended for boolean values (0/1) of selected or not, but not reliably for scores.
            It relies on each selected LED's value to be equal to its partner. 
    """
    print("Loading Results File")
    length = len(best_led_data)
    symmetry_count,non_symmetry_count = 0,0
    for j in range(int(length/2)):    
        upper = best_led_data [j][ column_index ]
        lower = best_led_data [(length-1) - j][ column_index ]
        #print str(j)+"  ;  "+str(upper)+"  ;  "+str(lower)
        if upper == lower:
            symmetry_count += 1
        else:
            non_symmetry_count += 1
            print (str(non_symmetry_count)+'). Non-symmetric pair: vertex ' + str(j) + ' (' + str(upper) + ') and corresponding symmetric vertex ' + str((length -1) -j)+ ' (' + str(lower) + ') are not matching.')
    symmetry_score = symmetry_count/(length/2)
    print("Results Symmetry Score (%): "+ str(symmetry_score))
