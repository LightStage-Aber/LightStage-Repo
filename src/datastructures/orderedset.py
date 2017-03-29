"""
ORDEREDSET (PYTHON RECIPE)

Set that remembers original insertion order.

Source: http://code.activestate.com/recipes/576694/
"""
import collections

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def __getitem__(self, x):
        assert( not isinstance(x, slice) ) # slicing not handled.
        return self.map[x] if x in self.map else None

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def size(self):
        return self.__len__()



class ListHashableOrderedSet(OrderedSet):
    """
    Wraps up an added item in a string type, making List objects hashable.
    NOTE: Iterable (__iter__) and reversed (__reversed__) will return keys as strings.
    """
    def __contains__(self, key):
        return super(ListHashableOrderedSet,self).__contains__(str(key))

    def add(self, key):
        super(ListHashableOrderedSet,self).add(str(key))

    def discard(self, key):
        super(ListHashableOrderedSet,self).discard(str(key))

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield eval(curr[0])
            curr = curr[2]
    
    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield eval(curr[0])
            curr = curr[1]
            
    def pop(self, last=True):
        return eval(super(ListHashableOrderedSet,self).pop(last))




def test_iterable_with_list_added_ListHashableOrderedSet():
    os = ListHashableOrderedSet()
    os.add([1,2]);
    for k in os:
        assert( type(k) is list )  # eval(k) will produce [1,2]
    assert( os.size() == 1 )
    assert( type(os.pop()) is list)
    assert( os.size() == 0 )



if __name__ == '__main__':
    s = OrderedSet('abracadaba')
    t = OrderedSet('simsalabim')
    print(s | t)
    print(s & t)
    print(s - t)
    print("\n\nTest ListHashableOrderedSet:")
    test_iterable_with_list_added_ListHashableOrderedSet()
    
