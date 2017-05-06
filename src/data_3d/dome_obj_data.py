"""
A module containing only the dome shape data, as adapted from the 'dome_c.obj' file.
        - get_dome_vertices()   returns the list of vertex coordinates. Each tuple is prepended by letter 'v' from the blender obj file.
        - get_dome_faces()      returns the list of faces as corresponding to numbered vertices. Each tuple is prepended by letter 'f' from the blender obj file.
"""


def get_dome_vertices():
    obj = [
        ('v', 0.0, 1.0, 0.0),
        ('v', 0.201774, 0.939234, 0.277718),
        ('v', 0.326477, 0.939234, -0.106079),
        ('v', 0.0, 0.939234, -0.343279),
        ('v', -0.326477, 0.939234, -0.106079),
        ('v', -0.201774, 0.939234, 0.277718),

        ('v', 0.403548, 0.727076, 0.555436),  # 6
        ('v', 0.57735, 0.794654, 0.187592),
        ('v', 0.652955, 0.727076, -0.212158),
        ('v', 0.356822, 0.794654, -0.491123),
        ('v', 0.0, 0.727076, -0.686557),
        ('v', -0.356822, 0.794654, -0.491123),
        ('v', -0.652955, 0.727076, -0.212158),
        ('v', -0.57735, 0.794654, 0.187592),
        ('v', -0.403548, 0.727076, 0.555436),
        ('v', 0.0, 0.794654, 0.607062),

        ('v', 0.525731, 0.447214, 0.723607),  # 16
        ('v', 0.730026, 0.514918, 0.449358),
        ('v', 0.854729, 0.514918, 0.06556),
        ('v', 0.850651, 0.447214, -0.276393),
        ('v', 0.652955, 0.514918, -0.555436),
        ('v', 0.326477, 0.514918, -0.792636),
        ('v', 0.0, 0.447214, -0.894427),  # 22
        ('v', -0.326477, 0.514918, -0.792636),
        ('v', -0.652955, 0.514918, -0.555436),
        ('v', -0.850651, 0.447214, -0.276393),
        ('v', -0.854729, 0.514918, 0.06556),
        ('v', -0.730026, 0.514918, 0.449358),
        ('v', -0.525731, 0.447214, 0.723607),
        ('v', -0.201774, 0.514918, 0.833155),
        ('v', 0.201774, 0.514918, 0.833155),

        ('v', 0.730026, 0.171639, 0.661515),  # 31
        ('v', 0.934172, 0.187592, 0.303531),
        ('v', 0.979432, 0.171639, -0.106079),
        ('v', 0.854729, 0.171639, -0.489876),
        ('v', 0.57735, 0.187592, -0.794654),
        ('v', 0.201774, 0.171639, -0.964275),
        ('v', -0.201774, 0.171639, -0.964275),
        ('v', -0.57735, 0.187592, -0.794654),
        ('v', -0.854729, 0.171639, -0.489876),
        ('v', -0.979432, 0.171639, -0.106079),
        ('v', -0.934172, 0.187592, 0.303531),
        ('v', -0.730026, 0.171639, 0.661515),
        ('v', -0.403548, 0.171639, 0.898715),
        ('v', 0.0, 0.187592, 0.982247),
        ('v', 0.403548, 0.171639, 0.898715),

        ('v', -0.403548, -0.171639, -0.898715),  # 46
        ('v', 0.0, -0.187592, -0.982247),
        ('v', 0.403548, -0.171639, -0.898715),
        ('v', 0.730026, -0.171639, -0.661515),
        ('v', 0.934172, -0.187592, -0.303531),
        ('v', 0.979432, -0.171639, 0.106079),
        ('v', 0.854729, -0.171639, 0.489876),
        ('v', 0.57735, -0.187592, 0.794654),
        ('v', 0.201774, -0.171639, 0.964275),
        ('v', -0.201774, -0.171639, 0.964275),
        ('v', -0.57735, -0.187592, 0.794654),
        ('v', -0.854729, -0.171639, 0.489876),
        ('v', -0.979432, -0.171639, 0.106079),
        ('v', -0.934172, -0.187592, -0.303531),
        ('v', -0.730026, -0.171639, -0.661515),

        ('v', -0.201774, -0.514918, -0.833155),  # 61
        ('v', 0.201774, -0.514918, -0.833155),
        ('v', 0.525731, -0.447214, -0.723607),
        ('v', 0.730026, -0.514918, -0.449358),
        ('v', 0.854729, -0.514918, -0.06556),
        ('v', 0.850651, -0.447214, 0.276393),
        ('v', 0.652955, -0.514918, 0.555436),
        ('v', 0.326477, -0.514918, 0.792636),
        ('v', 0.0, -0.447214, 0.894427),
        ('v', -0.326477, -0.514918, 0.792636),
        ('v', -0.652955, -0.514918, 0.555436),
        ('v', -0.850651, -0.447214, 0.276393),
        ('v', -0.854729, -0.514918, -0.06556),
        ('v', -0.730026, -0.514918, -0.449358),
        ('v', -0.525731, -0.447214, -0.723607),

        ('v', 0.0, -0.794654, -0.607062),  # 76
        ('v', 0.403548, -0.727076, -0.555436),
        ('v', 0.57735, -0.794654, -0.187592),
        ('v', 0.652955, -0.727076, 0.212158),
        ('v', 0.356822, -0.794654, 0.491123),
        ('v', 0.0, -0.727076, 0.686557),
        ('v', -0.356822, -0.794654, 0.491123),
        ('v', -0.652955, -0.727076, 0.212158),
        ('v', -0.57735, -0.794654, -0.187592),
        ('v', -0.403548, -0.727076, -0.555436),

        ('v', 0.201774, -0.939234, -0.277718),  # 86
        ('v', 0.326477, -0.939234, 0.106079),
        ('v', 0.0, -0.939234, 0.343279),
        ('v', -0.326477, -0.939234, 0.106079),
        ('v', -0.201774, -0.939234, -0.277718),

        ('v', 0.0, -1.0, -0.0)  # 91
    ]

    def apply_map(obj):
        global map_dome_to_obj
        actual = [0] * len(obj)
        # convert from virtual mappings onto the real dome vertex numbering
        for i in range(len(obj)):
            actual[i] = obj[map_dome_to_obj[i]]
        return actual
        # print actual

    def verify(actual, obj):
        # verify the data - all pairs of vertices should oppose each other
        # on the dome, so the coordinates should sum to zero
        for i in range(len(obj) / 2):
            diff = 0
            for j in range(1, 4):
                diff += actual[i][j] + actual[(len(obj) - 1) - i][j]
            assert (abs(diff) < 0.00001), "ERROR in vertex position mapping between vertices: "+str(i)+", "+str((len(obj)-1)-i)+". Diff = "+str(diff)
            # res = actual[i] + actual[(len(obj) - 1) - i]
        return actual

    return verify(apply_map(obj), obj)


map_dome_to_obj = [
    # convert an index on the dome file to the index in the obj
    (0),
    (2),
    (3),
    (4),
    (5),
    (1),
    (8),
    (9),
    (10),
    (11),
    (12),
    (13),
    (14),
    (15),
    (6),
    (7),
    (20),
    (21),
    (22),
    (23),
    (24),
    (25),
    (26),
    (27),
    (28),
    (29),
    (30),
    (16),
    (17),
    (18),
    (19),
    (34),
    (35),
    (36),
    (37),
    (38),
    (39),
    (40),
    (41),
    (42),
    (43),
    (44),
    (45),
    (31),
    (32),
    (33),
    (58),
    (59),
    (60),
    (46),
    (47),
    (48),
    (49),
    (50),
    (51),
    (52),
    (53),
    (54),
    (55),
    (56),
    (57),
    (72),
    (73),
    (74),
    (75),
    (61),
    (62),
    (63),
    (64),
    (65),
    (66),
    (67),
    (68),
    (69),
    (70),
    (71),
    (84),
    (85),
    (76),
    (77),
    (78),
    (79),
    (80),
    (81),
    (82),
    (83),
    (90),
    (86),
    (87),
    (88),
    (89),
    (91),

]

map_obj_to_dome = [
    # convert an index in obj file to the index on physical dome
    (0),
    (5),
    (1),
    (2),
    (3),
    (4),
    (14),
    (15),
    (6),
    (7),
    (8),
    (9),
    (10),
    (11),
    (12),
    (13),
    (27),
    (28),
    (29),
    (30),
    (16),
    (17),
    (18),
    (19),
    (20),
    (21),
    (22),
    (23),
    (24),
    (25),
    (26),
    (43),
    (44),
    (45),
    (31),
    (32),
    (33),
    (34),
    (35),
    (36),
    (37),
    (38),
    (39),
    (40),
    (41),
    (42),
    (49),
    (50),
    (51),
    (52),
    (53),
    (54),
    (55),
    (56),
    (57),
    (58),
    (59),
    (60),
    (46),
    (47),
    (48),
    (65),
    (66),
    (67),
    (68),
    (69),
    (70),
    (71),
    (72),
    (73),
    (74),
    (75),
    (61),
    (62),
    (63),
    (64),
    (78),
    (79),
    (80),
    (81),
    (82),
    (83),
    (84),
    (85),
    (76),
    (77),
    (87),
    (88),
    (89),
    (90),
    (86),
    (91)
]


def get_dome_faces():
    faces = [
        ('f', 1, 3, 4),
        ('f', 5, 1, 4),
        ('f', 3, 10, 4),
        ('f', 1, 2, 3),
        ('f', 6, 1, 5),
        ('f', 4, 12, 5),
        ('f', 10, 11, 4),
        ('f', 3, 9, 10),
        ('f', 2, 8, 3),
        ('f', 1, 6, 2),
        ('f', 6, 16, 2),
        ('f', 5, 14, 6),
        ('f', 12, 13, 5),
        ('f', 4, 11, 12),
        ('f', 11, 24, 12),
        ('f', 10, 22, 11),
        ('f', 9, 21, 10),
        ('f', 3, 8, 9),
        ('f', 8, 19, 9),
        ('f', 2, 7, 8),
        ('f', 16, 7, 2),
        ('f', 16, 31, 7),
        ('f', 6, 15, 16),
        ('f', 14, 15, 6),
        ('f', 14, 28, 15),
        ('f', 5, 13, 14),
        ('f', 13, 27, 14),
        ('f', 12, 25, 13),
        ('f', 24, 25, 12),
        ('f', 24, 39, 25),
        ('f', 11, 23, 24),
        ('f', 22, 23, 11),
        ('f', 22, 37, 23),
        ('f', 10, 21, 22),
        ('f', 21, 36, 22),
        ('f', 9, 20, 21),
        ('f', 19, 20, 9),
        ('f', 19, 34, 20),
        ('f', 8, 18, 19),
        ('f', 7, 18, 8),
        ('f', 7, 17, 18),
        ('f', 31, 17, 7),
        ('f', 31, 46, 17),
        ('f', 16, 30, 31),
        ('f', 15, 30, 16),
        ('f', 15, 29, 30),
        ('f', 28, 29, 15),
        ('f', 28, 43, 29),
        ('f', 14, 27, 28),
        ('f', 27, 42, 28),
        ('f', 13, 26, 27),
        ('f', 25, 26, 13),
        ('f', 25, 40, 26),
        ('f', 39, 40, 25),
        ('f', 39, 61, 40),
        ('f', 24, 38, 39),
        ('f', 23, 38, 24),
        ('f', 23, 37, 38),
        ('f', 37, 48, 38),
        ('f', 22, 36, 37),
        ('f', 36, 49, 37),
        ('f', 21, 35, 36),
        ('f', 20, 35, 21),
        ('f', 20, 34, 35),
        ('f', 34, 51, 35),
        ('f', 19, 33, 34),
        ('f', 18, 33, 19),
        ('f', 18, 32, 33),
        ('f', 17, 32, 18),
        ('f', 17, 46, 32),
        ('f', 46, 54, 32),
        ('f', 31, 45, 46),
        ('f', 30, 45, 31),
        ('f', 30, 44, 45),
        ('f', 29, 44, 30),
        ('f', 29, 43, 44),
        ('f', 43, 57, 44),
        ('f', 28, 42, 43),
        ('f', 42, 58, 43),
        ('f', 27, 41, 42),
        ('f', 26, 41, 27),
        ('f', 26, 40, 41),
        ('f', 40, 60, 41),
        ('f', 61, 60, 40),
        ('f', 61, 75, 60),
        ('f', 39, 47, 61),
        ('f', 38, 47, 39),
        ('f', 38, 48, 47),
        ('f', 48, 62, 47),
        ('f', 37, 49, 48),
        ('f', 49, 63, 48),
        ('f', 36, 50, 49),
        ('f', 35, 50, 36),
        ('f', 35, 51, 50),
        ('f', 51, 65, 50),
        ('f', 34, 52, 51),
        ('f', 33, 52, 34),
        ('f', 33, 53, 52),
        ('f', 32, 53, 33),
        ('f', 32, 54, 53),
        ('f', 54, 68, 53),
        ('f', 46, 55, 54),
        ('f', 45, 55, 46),
        ('f', 45, 56, 55),
        ('f', 44, 56, 45),
        ('f', 44, 57, 56),
        ('f', 57, 71, 56),
        ('f', 43, 58, 57),
        ('f', 58, 72, 57),
        ('f', 42, 59, 58),
        ('f', 41, 59, 42),
        ('f', 41, 60, 59),
        ('f', 60, 74, 59),
        ('f', 75, 74, 60),
        ('f', 75, 85, 74),
        ('f', 61, 76, 75),
        ('f', 47, 76, 61),
        ('f', 47, 62, 76),
        ('f', 62, 86, 76),
        ('f', 48, 63, 62),
        ('f', 63, 77, 62),
        ('f', 49, 64, 63),
        ('f', 50, 64, 49),
        ('f', 50, 65, 64),
        ('f', 65, 78, 64),
        ('f', 51, 66, 65),
        ('f', 52, 66, 51),
        ('f', 52, 67, 66),
        ('f', 53, 67, 52),
        ('f', 53, 68, 67),
        ('f', 68, 80, 67),
        ('f', 54, 69, 68),
        ('f', 55, 69, 54),
        ('f', 55, 70, 69),
        ('f', 56, 70, 55),
        ('f', 56, 71, 70),
        ('f', 71, 82, 70),
        ('f', 57, 72, 71),
        ('f', 72, 83, 71),
        ('f', 58, 73, 72),
        ('f', 59, 73, 58),
        ('f', 59, 74, 73),
        ('f', 74, 84, 73),
        ('f', 85, 84, 74),
        ('f', 85, 90, 84),
        ('f', 75, 86, 85),
        ('f', 86, 75, 76),
        ('f', 62, 77, 86),
        ('f', 77, 91, 86),
        ('f', 63, 78, 77),
        ('f', 78, 63, 64),
        ('f', 65, 79, 78),
        ('f', 66, 79, 65),
        ('f', 66, 80, 79),
        ('f', 80, 66, 67),
        ('f', 68, 81, 80),
        ('f', 69, 81, 68),
        ('f', 69, 82, 81),
        ('f', 82, 69, 70),
        ('f', 71, 83, 82),
        ('f', 83, 89, 82),
        ('f', 72, 84, 83),
        ('f', 84, 72, 73),
        ('f', 90, 83, 84),
        ('f', 90, 89, 83),
        ('f', 90, 92, 89),
        ('f', 85, 91, 90),
        ('f', 91, 85, 86),
        ('f', 77, 87, 91),
        ('f', 78, 87, 77),
        ('f', 78, 79, 87),
        ('f', 79, 88, 87),
        ('f', 80, 88, 79),
        ('f', 80, 81, 88),
        ('f', 81, 89, 88),
        ('f', 89, 81, 82),
        ('f', 92, 88, 89),
        ('f', 92, 87, 88),
        ('f', 92, 91, 87),
        ('f', 92, 90, 91)
    ]

    def apply_map(faces):
        global map_obj_to_dome
        # convert each vertex of each face to the actual dome mapping
        for f in range(len(faces)):
            faces[f] = ('f',
                        map_obj_to_dome[faces[f][1] - 1] + 1,
                        map_obj_to_dome[faces[f][2] - 1] + 1,
                        map_obj_to_dome[faces[f][3] - 1] + 1
                        )
            return faces
    faces = apply_map(faces)
    faces = [x[1:] for x in faces]  # Remove 'f' from each tuple.
    return faces
