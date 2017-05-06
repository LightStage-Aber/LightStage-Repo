from numbers import Number

class BestFirstSearch():
    def __init__(self, threshold=-1, max_local_iterations=100):
        self.threshold = threshold
        self.max_local_iterations = max_local_iterations
        assert isinstance(self.threshold, Number) and self.threshold >= 0.0, \
            "Residual error threshold should be positive float: " + str(self.threshold) + ". Type: "+str(type(self.threshold))
        assert isinstance(self.max_local_iterations, Number) and self.max_local_iterations >= 1, \
            "Max search iterations should be positive int: " + str(self.max_local_iterations) + ". Type: " + str(type(self.max_local_iterations))

    def search(self, starting_value=0, starting_data={}):
        x = starting_value
        data = starting_data
        default_value = 9999999999999999
        find_minimum = {'value': default_value, 'data': data, 'count': 0}
        rounds = 0
        while x > self.threshold:  # Exit when threshold reached
            rounds += 1

            # Do update and evaluation, with corresponding data:
            x, data = self.update(x, data)

            # Store only best result:
            if x < find_minimum['value']:
                find_minimum = {'value': x, 'data': data, 'count': rounds}

            # Exit when we have been stuck on best value for max_iterations (and only when not
            elif find_minimum['value'] != default_value \
                    and find_minimum['count'] + self.max_local_iterations < rounds:
                find_minimum['rounds'] = rounds
                break

        return find_minimum

    def update(self, x, data):
        """
        Override in derived class with updated evaluation/update function.
        """
        x += 1
        data = {}
        return x, data


def search_user():
    s = BestFirstSearch(threshold=-1, max_local_iterations=100)
    find_minimum = s.search(starting_value=0, starting_data={})

    best_value = find_minimum['value']
    best_data = find_minimum['data']
    best_count = find_minimum['count']
    best_rounds = find_minimum['rounds']

    print best_value
    print best_data
    print best_count
    print best_rounds


if __name__ == "__main__":
    search_user()