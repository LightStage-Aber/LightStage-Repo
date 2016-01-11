import dome_obj_data

class Updateable_Line:
    def __init__(self, scale=8):
        self.index = 50
        self.min = 0
        self.max = len(dome_obj_data.get_dome_vertices())-1
        self.scale = scale
        self.__internal_set()    
    def __internal_set(self):
        v = dome_obj_data.get_dome_vertices()[self.index][1:]
        v = [ x * self.scale for x in v ]
        self.UPD_X, self.UPD_Y, self.UPD_Z = v[0],v[1],v[2] #1.0,1.0,1.0
    def set_xyz(self, x,y,z):
        self.UPD_X, self.UPD_Y, self.UPD_Z = x,y,z
    def decrement(self):
        self.index = self.max if self.index == self.min else self.index -1
        self.__internal_set()
    def increment(self):
        self.index = self.min if self.index == self.max else self.index +1
        self.__internal_set()
    def get_xyz(self):
        return self.UPD_X, self.UPD_Y, self.UPD_Z
    def get_point(self):
        return (self.UPD_X, self.UPD_Y, self.UPD_Z)
    def get_index(self):
        return self.index
