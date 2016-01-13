import os,sys

class ParseError(Exception): pass;
class TestFailedError(Exception): pass;


    
def get_all_vertex_face_objects( filename ):
    v = read_vertices_objects( filename )
    f = read_faces_objects( filename )
    return v,f

def get_all_object_triangles( filename, scale ):
    vertexObjs     = read_vertices_objects( filename )
    faceObjs       = read_faces_objects( filename )

    r = []
    j = 0
    
    # Validation:
    vertices, faces = [],[]
    for obj in range(len(vertexObjs)):
        vertices += vertexObjs[obj]
        faces    += faceObjs[obj]
    max_vertex_index = max([max(x) for x in faces])
    if len(vertices) != max_vertex_index:
        print "ParseWarning: A face's vertex index number is does not match the quantity of read vertices."
        print "Qty of Vertices: "+str(len(vertices))+", Largest Face Index: "+str(max_vertex_index)
            
    # Parse as Tris:
    for obj in range(len(vertexObjs)):
        vertices = vertexObjs[obj]
        faces    = faceObjs[obj]
        r.append([])
        c = 0
        for f in faces:     # for every face
                for i in f: # for each index point in face
                        c+=1
                        try:
                            v = vertices[i-1]
                        except IndexError as indErr:
                            print "IndexError: Attempted to access index: "+str(i-1)+" in list of length: "+str(len(vertices))
                            raise IndexError
                        tmpv = [v[0]*scale, v[1]*scale, v[2]*scale]
                        r[j].append(tmpv)
                        if c % 3 == 0:
                                j+=1
                                r.append([])        
        r = r[:len(r)-1]    # remove the final empty list.
    """ Returns a list of lists of lists. The final list has 3 values. The mid-list has 3 vertices.
        The first list contains all the triangles.
    """
    return r


def apply_translate( triangles, translate_tris=(0,0,0) ):
    """ Apply a translation to each triangle's points.
        -- No validation checking.
    """
    for i in range(len(triangles)):                 # each tri in triangles
        for j in range(len(triangles[i])):          # each point in a tri
            for k in range(len(translate_tris)):    # each axis in a point
                triangles[i][j][k] = float(triangles[i][j][k]) + float(translate_tris[k])
    


def read_vertices_objects(filename):    
    object_vertices = []
    prev_line = "#"
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            for line in f:
                line        = line.strip()
                line        = list(line.split())                   # split to list
                is_valid_data_block         = len(line) > 0
                if is_valid_data_block:
                    cmd      = line[0]
                    values   = line[1:]                           # get only values
                    prev_cmd = prev_line[0] if len(prev_line) > 0 else "#"
                    is_first_vertex         = (cmd == 'v' and prev_cmd != "v")
                    is_subsequent_vertex    = (cmd == 'v' and prev_cmd == "v")
                    is_final_vertex         = (cmd != 'v' and prev_cmd == "v")
                    if is_first_vertex:
                        object_vertices.append([])
                    if is_first_vertex or is_subsequent_vertex:
                        values   = [float(x) for x in values]   # cast from string to float
                        object_vertices[len(object_vertices)-1].append( values )
                prev_line = line
    return object_vertices

def read_faces_objects( filename ):
    object_faces = []
    prev_line = "#"
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            count = -1
            for line in f:
                count +=1
                line = line.strip()
                is_valid_data_block         = len(line) > 0
                if is_valid_data_block:
                    cmd      = line[0]
                    prev_cmd = prev_line[0] if len(prev_line) > 0 else "#"
                    is_first_face         = (cmd == 'f' and prev_cmd != "f")
                    is_subsequent_face    = (cmd == 'f' and prev_cmd == "f")
                    is_final_face         = (cmd != 'f' and prev_cmd == "f")
                    if is_first_face:
                        object_faces.append([])
                    if is_first_face or is_subsequent_face:
                        line = line.replace("-","")             # remove negative index values.
                        line = line.replace("-","")             # remove negative index values.
                        values   = list(line.split())           # split to list
                        values   = values[1:]                   # get only values
                        for x in values:
                            # Formatting note: f  1//1 2//2 3//3    -- position vertex/texture coordinate/normal vertex
                            x = x.split("/")
                            if len(x) < 1:
                                print "An .obj file face entry exists without a position-vertex point, expected format: 'position-vertex/texture-coordinate/normal-vertex'"
                                print "Line "+str(count)+":\n"+str(line)
                                raise ValueError
                        values   = [int(x.split("/")[0]) for x in values]     # cast from string to int (index)
                        object_faces[len(object_faces)-1].append( values )
                prev_line = line
    return object_faces



def test(filename, expected={"v":0,"f":0,"tri":0}):
    f = filename
    if not os.path.exists( f ):
        raise TestFailedError("File does not exist: "+str(f))
    v = read_vertices_objects( f )
    actual = len(v)
    if expected['v'] != actual:
        raise TestFailedError("Qty of vertices incorrect. "+str(expected['v'])+"; "+str(actual))
        
    v = read_faces_objects( f )
    actual = len(v)
    if expected['f'] != actual:
        raise TestFailedError("Qty of faces incorrect. "+str(expected['f'])+"; "+str(actual))
    
    tris = get_all_object_triangles( f, scale=1 )
    actual = len(tris)
    if expected['tri'] != actual:
        raise TestFailedError("Qty of faces incorrect. "+str(expected['tri'])+"; "+str(actual))
    return True
    
    
if __name__ == "__main__":
    #house_plant = "../../models/house plant 2/house plant.obj"
    plants3 = "../models/Flower/plants3.obj"
    dome    = "../models/dome_c.obj"
    wheat   = "../models/wheat/wheat1.obj"
    
#    if test(plants3, expected={"v":381,"f":381,"tri":12290}):
#        print ("Passed:", plants3)
#    if test(dome, expected={"v":1,"f":1,"tri":180}):
#        print ("Passed:", dome)
    if test(wheat, expected={"v":1,"f":2,"tri":11566}):
        print ("Passed:", wheat)
    
    
