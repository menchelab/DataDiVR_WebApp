from os import link
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create a 3D figure


name = "bunny2"
f = open("python_tools/" +name + ".obj", "r")
lines = f.readlines()
verticis = []
polygons = []
linklist = []
nLinkList = []
#read obj file

for i in lines:
    
    if i[0] == "v" and i[1] == " ":
        
        i = i.rstrip()
        i = i[1:]  # delete first 3 chars
        i = i.lstrip()
        verts = list(i.split(" "))
        
        verticis.append(verts)
        

    if i[0] == "f" and i[1] == " ":
        i = i.rstrip()
        i = i[1:]  # delete first 3 chars
        i = i.lstrip()
        links = list(i.split(" "))
        
        poly = []

        for l in links:
            x = list(l.split("/"))
            poly.append(x[0])
        polygons.append(poly)    

# normalize verticis to 0 - 1

minvals = [999990.0,999990.0,999990.0]
maxvals = [-999990.0,-999990.0,-999990.0]
dimen = [0.0,0.0,0.0]
normverts = []
x = []
y = []
z = []

for v in verticis:
#    x.append(float(v[0]))
#    y.append(float(v[1]))
#    z.append(float(v[2]))
    for i in range(3):
        if float(v[i]) < minvals[i]:
            minvals[i] = float(v[i])

        if float(v[i]) > maxvals[i]:
            maxvals[i] = float(v[i])

print(minvals)
print(maxvals)

dimen[0] = maxvals[0] - minvals[0]
dimen[1] = maxvals[1] - minvals[1]
dimen[2] = maxvals[2] - minvals[2]

biggest = 0.0

for i in range(3):
    
    if sum([float(dimen[i])]) > biggest:
        biggest = dimen[i]

print(dimen)
print(biggest)


for v in verticis:
    thisv = [0.0,0.0,0.0]
    for i in range(3):
        thisv[i] = (float(v[i]) - minvals[i]) / biggest
    x.append(float(thisv[0]))
    y.append(float(thisv[1]))
    z.append(float(thisv[2]))
    normverts.append(thisv)

#print(normverts)

# make links from polygons


for p in polygons:
    c = 0 
    for i in p:
        next = (c + 1) % len(p) 
        p1 = int(i) - 1
        p2 = int(p[next]) - 1
        if p1 > p2:
            textLink = str(p2) + " " + str(p1)
        else:
            textLink = str(p1) + " " + str(p2)

        nLinkList.append(textLink)
        
        c = c + 1

# remove duplicates
final_linklist = list(dict.fromkeys(nLinkList))

print(str(len(linklist)) + "after removing dublicates: " + str(len(final_linklist)))

for i in final_linklist:
    tlink = list(i.split(" "))
    thislink = [int(tlink[0]), int(tlink[1])]
    linklist.append(thislink)




i = 0
with open(name +'_nodes.csv', 'w') as f:
    for l in normverts:
        line = str(l[0]) + ',' + str(l[1])+ ',' + str(l[2]) +"\n"
        f.write(line)
        i = i + 1
f.close()

with open(name +'_links.csv', 'w') as f:
    for l in linklist:
        line = str(l[0]) + ',' + str(l[1]) +"\n"
        f.write(line)
f.close()
'''
with open(name +'_nodes.csv', 'w') as f:
    for l in normverts:
        line = str(l[0]) + ',' + str(l[1])+ ',' + str(l[2]) + ",255,255,0,100,node" + str(i) +";vertex" +"\n"
        f.write(line)
        i = i + 1
f.close()
'''
print(str(len(normverts)) + " verticies")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the point cloud data
ax.scatter(x, y, z, s=1)

# Set the axis labels
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# Show the plot
plt.show()