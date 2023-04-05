from os import link

name = "dna"
f = open(name + ".txt", "r")
lines = f.readlines()
verticis = []

for i in lines:
    verts = list(i.split(" "))
    print(verts)
    verticis.append(verts)


# normalize verticis to 0 - 1

minvals = [9990.0,9990.0,9990.0]
maxvals = [-9990.0,-9990.0,-9990.0]
dimen = [0.0,0.0,0.0]
normverts = []
print(verticis)
for v in verticis:
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

biggest = 0

for d in dimen:
    if d > biggest:
        biggest = d

print(dimen)
print(biggest)


for v in verticis:
    thisv = [0.0,0.0,0.0]
    for i in range(3):
        thisv[i] = (float(v[i]) - minvals[i]) / biggest
    normverts.append(thisv)

#print(normverts)

# make links from polygons




i = 0
with open(name +'nodes.csv', 'w') as f:
    for l in normverts:
        line = str(l[0]) + ',' + str(l[1])+ ',' + str(l[2]) + ",255,255,0,100,node" + str(i) +";vertex" +"\n"
        f.write(line)
        i = i + 1
f.close()

print(str(len(normverts)) + " verticies")