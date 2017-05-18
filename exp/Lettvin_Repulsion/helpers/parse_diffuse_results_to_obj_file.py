"""
    Module to parse a Lettvin Results File C array of vertex points (and distances) into an OBJ file format of vertex points.
    
    arg1: the path to the results file. (File must exist)
    arg2: the file extension of the output OBJ filename. (e.g. ".obj") Default is ".obj" (File must not exist)
    
    Vertex points are written in the OBJ file format, as they are found in the result file.
    
    WARNING:
        - The faces of the OBJ file are not known and are therefore are written to the OBJ file as a single triangle, from vertices 1,2,3.
"""

import sys, os

# Check input file exists:
path = sys.argv[1]
assert os.path.exists( path ) , "Input file does not exist, aborting.\nFilename: "+str(path)

file_extension = sys.argv[2] if sys.argv[2] == "" else ".obj"
assert not os.path.exists( path+file_extension ), "Output file already exists, aborting.\nFilename: "+str(path+file_extension)

# extract the c array of vertex points from result file:
l = []
with open(path, 'rb') as f:
  c = 0
  for line in f:
    if line.strip().startswith("{"):
      l.append( line.strip() )
      c+=1

# convert string of c array to python list
positions = eval("["+("".join(l)).replace("{","[").replace("}","]")+"]")

# remove different value
pos = [x[0:3] for x in positions]

# prepare the Obj file format header and content:
w = []
w.append("""# Blender v2.69 (sub 0) OBJ File: '"""+path+"""'
www.blender.org
mtllib positions_diffuse.mtl
o """+path)

for x in pos:
  w.append("v "+str(x[0])+" "+str(x[1])+" "+str(x[2]))

# include an arbitrary face to hide file format parse errors later..
w.append("""usemtl None
s off
f 1 2 3""")

# write out the obj file:
f = open(str(path)+str(file_extension),'w')
for s in w:
  f.write( str(s) +"\n")


