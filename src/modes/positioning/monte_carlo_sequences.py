import random as rnd


###################################################### Random Generation of LEDs sequences
dict_random = {}


def is_already_tested( led_seq ):
	""" Returns false, if argument is a new LED sequence. Otherwise, true.
	"""
	is_already_tested = False
	test_l = sorted(led_seq)
	if str(test_l) not in dict_random:
		# do it ..
		dict_random[str(test_l)] = 1;
		#print("Is new "+str(test_l))
	else:
		#print("Is in "+str(test_l))
		is_already_tested = True
	return is_already_tested

def get_random_set( num_of_leds, total_num_leds ):
	""" Returns a set (no duplicates) of LED index numbers.
	"""
	known_led_indexes = range(total_num_leds)
	new_sequence = []
	while len(new_sequence) < num_of_leds:
		i = rnd.randint(0,len(known_led_indexes)-1)
		led = known_led_indexes[i]
		new_sequence.append(led)
		del(known_led_indexes[i])
	return new_sequence

def get_new_set( num_of_leds=44, total_num_leds=92 ):
	""" Returns a new set of LED index numbers.
	"""
	c = 0
	seq1 = get_random_set( num_of_leds, total_num_leds )
	while is_already_tested( seq1 ):
		seq1 = get_random_set( num_of_leds, total_num_leds )
		c +=1 
		#print( str(c)+" test..." )
	return seq1

def get_random_led_index_sets( num_of_leds=44, total_num_leds=92 ):
	l = []
	for i in range(15000):
		s = get_new_set( num_of_leds, total_num_leds )
		l.append( s ) 
		#print "----Working on set: "+str(i)
	return l
	
def get_random_led_sequence_sets(all_leds, num_of_leds = 44, total_num_leds=92):
	led_index = get_random_led_index_sets(num_of_leds, total_num_leds)
	led_sets = []
	for led_index_set in led_index:
		led_set = [] 
		for index in led_index_set:
		    led_set.append(all_leds[index])
		led_sets.append(led_set)
	return led_sets


################# Generate sequences with a previous set already compute, we reorganised the set with replacing best LEDs and non selected one



dict_recursive_search = {}

def get_led_sets_selected(all_leds, led_sequence, sequence_size, max_depth, index_stop_search = -1):
    if(index_stop_search == -1):
        index_stop_search = len(led_sequence) - sequence_size
    print("Get led sets: " + str((sequence_size, led_sequence, all_leds)) + "\n")
    print

    all_sequence    = [] #The sequence returned sorted
    new_sequence    = all_leds[:]
    new_led_sequence = led_sequence[:]
    all_sequence = recursive_set(new_sequence, new_led_sequence, sequence_size-1, all_sequence, sequence_size, max_depth, index_stop_search)
    print(str(len(all_sequence)) + " Sequences")
    return all_sequence


def recursive_set(all_leds, led_sequence, level, all_sequence, sequence_size, max_depth, index_stop_search):
    """
    1 = 92 leds 
    2 = current 6 (44) ideal leds
    3 = current search depth
    4 = all found led sequences (starting with best set of test 6 or real 44)
    5 = required led sequence sequence_size e.g. 44
    6 = max depth 
    7 = number of led on the right of sequence size to test
    """
    if(level == 0):
        length = len(led_sequence)
        new_sequence = []
        new_led_sequence = led_sequence[:]
        new_led_sequence = new_led_sequence[0:sequence_size]
        sequence_key = sorted(new_led_sequence)
        if str(sequence_key) not in dict_recursive_search:
            # do it ..
            for led_index in new_led_sequence:
                new_sequence.append(all_leds[led_index])
            all_sequence.append(new_sequence)
            dict_recursive_search[str(sequence_key)] = 1;
            #print("Is new "+str(sequence_key))
        #print(new_led_sequence)
        for index in range(sequence_size, sequence_size + index_stop_search):
            new_sequence = []
            new_led_sequence = led_sequence[:]
            temp = new_led_sequence[sequence_size-1]
            new_led_sequence[sequence_size-1] = new_led_sequence[index]
            new_led_sequence[index] = temp
            #decalage valeur
            new_led_sequence = new_led_sequence[0:sequence_size]

            """if i > 5:
                break"""

            #print(new_led_sequence)
            sequence_key = sorted(new_led_sequence)
            if str(sequence_key) not in dict_recursive_search:
                for led_index in new_led_sequence:
                    new_sequence.append(all_leds[led_index])
                all_sequence.append(new_sequence)
                dict_recursive_search[str(sequence_key)] = 1;
                #print("Is new "+str(sequence_key))
            
    elif(level > 0 and level < max_depth):
        length = len(led_sequence)
        new_sequence = []
        new_led_sequence = led_sequence[:]
        all_sequence = recursive_set(all_leds, new_led_sequence, level - 1, all_sequence, sequence_size, max_depth, index_stop_search)
        for index in range(sequence_size-level, sequence_size + index_stop_search):
            new_sequence = []
            new_led_sequence = led_sequence[:]
            
            temp = led_sequence[sequence_size]
            new_led_sequence[index] = led_sequence[sequence_size-1-level]
            new_led_sequence[sequence_size-1-level] = led_sequence[index]
            #decalage valeur
            all_sequence = recursive_set(all_leds, new_led_sequence, level-1, all_sequence, sequence_size, max_depth, index_stop_search)
    else:
        all_sequence = recursive_set(all_leds, led_sequence, level-1, all_sequence, sequence_size, max_depth, index_stop_search)
   
    return all_sequence





##################################################TEST FOR SIMPLEXE



