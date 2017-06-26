
class coverage_datastructure:
    """ With separated rotations and camera positions.
    """
    def __init__( self ):
        self.map = {}
    def add(self, angle, rotation_num, cam_num, led_num, tri_num ): 
        if rotation_num not in self.map:
            self.map[rotation_num] = {}
        if cam_num not in self.map[rotation_num]:
            self.map[rotation_num][cam_num] = {}
        if led_num not in self.map[rotation_num][cam_num]:
            self.map[rotation_num][cam_num][led_num] = {}
        if tri_num not in self.map[rotation_num][cam_num][led_num]:
            self.map[rotation_num][cam_num][led_num][tri_num] = angle
    def get(self, rotation_num, cam_num ):
        return self.map[rotation_num][cam_num]


class accumulated_coverage_datastructure:
    """ With shading scores for shading per tri, from each led, 
        to be accumulated over rotations and camera viewpoints.
    """
    def __init__( self ):
        self.map = {}
    def add(self, score, led_num, tri_num ): 
        if led_num not in self.map:
            self.map[led_num] = {}
        if tri_num not in self.map[led_num]:
            self.map[led_num][tri_num] = score
    def get(self):
        return self.map


def test():
    x  = coverage_datastructure()
    x.add( angle=100, rotation_num=1, cam_num=1, led_num=1, tri_num=1 )
    z = x.get( rotation_num=1, cam_num=1 )

def test_accumulated():
    x  = accumulated_coverage_datastructure()
    x.add( score=100, led_num=1, tri_num=1 )
    z = x.get()


if __name__ == "__main__":
    test_accumulated()
