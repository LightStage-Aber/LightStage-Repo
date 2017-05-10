default_path = "../src/"
import sys
sys.path.insert(0, default_path)

from helpers.test_support_pipe_capture import captured_stdout
import unittest

from data_3d import obj_model_reader

class Test_DomeModel(unittest.TestCase):

    def __init__(self, *args, **kwords):
        unittest.TestCase.__init__(self, *args, **kwords)
        filename = "../models/dome/dome_c.obj"
        obj_object_index = 0
        self._vertices  = obj_model_reader.read_vertices_objects(filename)[obj_object_index]
        self._faces     = obj_model_reader.read_faces_objects(filename)[obj_object_index]

    def test_number_of_faces(self):
        """"""
        actual = len(self._faces)
        expected = 180
        self.assertTrue(actual == expected)

    def test_number_of_vertices(self):
        actual = len(self._vertices)
        expected = 92
        self.assertTrue(actual == expected)

    def test_number_of_edges(self):
        edges_per_face = [(0,1),(1,2),(2,0)]
        d = {}
        for f in self._faces:
            for e in edges_per_face:
                edge_pair_key = str(f[e[0]]) + "_" + str(f[e[1]])
                d[edge_pair_key] = 1
        actual = len(d)
        expected = 540
        self.assertTrue( actual == expected )


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    unittest.TextTestRunner(verbosity=3).run(suite)
