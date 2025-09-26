
import random
import numpy as np
import os
import json
import cv2




# LOAD PROJECT DATA
def dataDiVR2obj(pfile):
    
    pname = pfile["name"]
    count = 0
    for tex in pfile["layouts"]:

        links = {}
        nodes = {}
        npos = []
        nweight = []
        lweight = []
        ns = 0.5
        ls = 0.03

        with open("static/projects/"+pname+"/nodes.json") as f:
            nodes = json.load(f)



        with open("static/projects/"+pname+"/links.json") as f:
            links = json.load(f)

        #print(pfile["nodecount"])
        #print(nodes)


        img = cv2.imread("static/projects/"+pname+"/layouts/"+tex+".bmp")
        imgl = cv2.imread("static/projects/"+pname+"/layoutsl/"+tex+"l.bmp")

        for i in range(int(pfile["nodecount"])):
            y = i % 128
            x = int(i/128)
            h = img[x,y]
            l = imgl[x,y]
            npos.append( [(img[x,y][0]*256+imgl[x,y][0])/655.36,(img[x,y][1]*256+imgl[x,y][1])/655.36,(img[x,y][2]*256+imgl[x,y][2])/655.36])
            if "w" in nodes["nodes"][i]:
                nweight.append(ns * nodes["nodes"][i]["w"])
            else:
                nweight.append(ns)


        Cverts =[[-0.5, -0.5, -0.5],[-0.5, 0.5, -0.5],[0.5, 0.5, -0.5],[0.5, -0.5, -0.5],[-0.5, -0.5, 0.5],[0.5, -0.5, 0.5],[0.5, 0.5, 0.5],[-0.5, 0.5, 0.5]]
        CUVs=[[0,0],[0.0078125,0],[0.0078125,0.0078125],[0,0.0078125]]
        Ctriangles=[[0,1,2,3],[4,5,6,7],[0,3,5,4],[3,2,6,5],[2,1,7,6],[1,0,4,7]]
        CtrianglesUV=[[0,1,2,3],[3,0,1,2],[3,0,1,2],[3,0,1,2],[3,0,1,2],[3,0,1,2]]

        verts = []
        UVs = []
        triangles = []
        trianglesUV = []

        nc = pfile["nodecount"]
        lc = len(links["links"])



        for i in range (nc):

            voffset = i * len(Cverts)
            uoffset = i * len(CUVs)
            uv = [i%128, 127 -int(i/128)]
            pos = npos[i]

            for v in Cverts:
                verts.append([v[0]* nweight[i] +pos[0],v[1]* nweight[i] +pos[1], v[2]* nweight[i] +pos[2]])
            for u in CUVs:
                UVs.append([u[0]+uv[0]/128, u[1]+uv[1]/128])
            for t in Ctriangles:
                triangles.append([t[0]+ voffset, t[1]+ voffset, t[2]+ voffset, t[3]+ voffset])
            for x in CtrianglesUV:
                trianglesUV.append([x[0]+ uoffset, x[1]+ uoffset, x[2]+ uoffset, x[3]+ uoffset])



        #linklist = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 13], [13, 14], [14, 15], [15, 16], [16, 17], [17, 18], [18, 19], [19, 20], [20, 21], [21, 22], [22, 23], [23, 24], [24, 25], [25, 26], [26, 27], [27, 28], [28, 29], [29, 30], [30, 31], [31, 32], [32, 33], [33, 34], [34, 35], [35, 36], [36, 37], [37, 38], [38, 39], [39, 40], [40, 41], [41, 42], [42, 43], [43, 44], [44, 45], [45, 46], [46, 47], [47, 48], [48, 49], [49, 50], [50, 51], [51, 52], [52, 53], [53, 54], [54, 55], [55, 56], [56, 57], [57, 58], [58, 59], [59, 60], [60, 61], [61, 62], [62, 63], [63, 64], [64, 65], [65, 66], [66, 67], [67, 68], [68, 69], [69, 70], [70, 71], [71, 72], [72, 73], [73, 74], [74, 75], [75, 76], [76, 77], [77, 78], [78, 79], [79, 80], [80, 81], [81, 82], [82, 83], [83, 84], [84, 85], [85, 86], [86, 87], [87, 88], [88, 89], [89, 90], [90, 91], [91, 92], [92, 93], [93, 94], [94, 95], [95, 96], [96, 97], [97, 98], [98, 99], [99, 100]]
        linklist = []
        for l in links["links"]:
            
            thisl = [l["s"],l["e"]]
            linklist.append(thisl)
            if "w" in l:
                lweight.append(ls * l["w"])
            else:
                lweight.append(ls)

        Lverts = []
        LUVs = []
        Ltriangles = []
        LtrianglesUV = []

        i = 0

        nverts = len(verts)
        nuv = len(UVs)
        print(len(linklist))
        for l in linklist:
            scale = lweight[i]
            #a = np.random.randn(3)
            #b = np.random.randn(3)
            a = np.array(npos[int(l[0])])
            b = np.array(npos[int(l[1])])
            #b = np.array([[0.0, 1.0, 0.0],[1.0, 0.0, 0.0],[0.0, 0.0, 1.0]])
            c = a - b
            p = b + c/2

            k = c/np.linalg.norm(c)
            l = np.linalg.norm(c)
            #y = np.cross(c, [0,0,1])
            #print(l)
            #print (np.dot(a,b))
            #k = np.array([ 0.59500984,  0.09655469, -0.79789754])
            x = np.random.randn(3)  # take a random vector
            x -= x.dot(k) * k / np.linalg.norm(k)**2      # make it orthogonal to k
            x /= np.linalg.norm(x)
            y = np.cross(k, x)
            m = np.array([k*l,x*scale,y*scale])
            #print(m)


            voffset = i * len(Cverts)
            uoffset = i * len(CUVs)
            uv = [i%512, 512 -int(i/512)]
            pos = p
            

            for v in Cverts:
                vr = np.dot(v,m)
                verts.append([vr[0]+pos[0],vr[1]+pos[1], vr[2]+pos[2]])
            for u in CUVs:
                UVs.append([u[0]/4+uv[0]/512, u[1]*2+uv[1]/64-7.015625] )
            for t in Ctriangles:
                Ltriangles.append([t[0]+ voffset + nverts, t[1]+ voffset + nverts, t[2]+ voffset + nverts, t[3]+ voffset + nverts])
            for x in CtrianglesUV:
                LtrianglesUV.append([x[0]+ uoffset + nuv, x[1]+ uoffset + nuv, x[2]+ uoffset + nuv, x[3]+ uoffset + nuv])
            i += 1


        name = "static/projects/"+pname+"/"+ str(count) +".obj"
        if os.path.isfile(name):
            open(name, 'w').close()
        with open(name, 'a') as f1:
            for v in verts:
                line = "v " + str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + '\n'
                f1.write(line)
            for u in UVs:
                line = "vt " + str(u[0]) + " " + str(u[1]) +'\n'
                f1.write(line)

            f1.write('\ng nodes'+str(count)+'\nusemtl nodes''\n')
            c = 0
            for t in triangles:
                    line = "f " + str(t[0] +1) + "/" +str(trianglesUV[c][0] +1) + " "+ str(t[1] +1) + "/" +str(trianglesUV[c][1] +1) +" "+ str(t[2] +1) + "/"+ str(trianglesUV[c][2] +1)  +" "+ str(t[3] +1) + "/"+ str(trianglesUV[c][3] +1) + '\n'
                    f1.write(line)
                    c+=1


            f1.write('\ng links'+str(count)+'\nusemtl links''\n')
            c = 0
            for t in Ltriangles:
                    line = "f " + str(t[0] +1) + "/" +str(LtrianglesUV[c][0] +1) + " "+ str(t[1] +1) + "/" +str(LtrianglesUV[c][1] +1) +" "+ str(t[2] +1) + "/"+ str(LtrianglesUV[c][2] +1)  +" "+ str(t[3] +1) + "/"+ str(LtrianglesUV[c][3] +1) + '\n'
                    f1.write(line)
                    c+=1
        count += 1
        print(count)


pfile = {}
pname = "bunny1"

with open("static/projects/"+pname+"/pfile.json") as f:
    pfile = json.load(f)

dataDiVR2obj(pfile)