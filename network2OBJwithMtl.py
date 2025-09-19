import random
import numpy as np
import os
import json
import cv2

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

        img_path = "static/projects/"+pname+"/layouts/"+tex+".bmp"
        imgl_path = "static/projects/"+pname+"/layoutsl/"+tex+"l.bmp"
        img = cv2.imread(img_path)
        imgl = cv2.imread(imgl_path)
        
        img_rgb_path = "static/projects/" + pname + "/layoutsRGB/" + tex + ".png"
        img_rgb = cv2.imread(img_rgb_path, cv2.IMREAD_UNCHANGED)
        if img_rgb is None:
            raise FileNotFoundError(f"Could not load RGBA layout image at {img_rgb_path}")

        img_links_rgb_path = "static/projects/" + pname + "/linksRGB/" + tex + ".png"
        img_links_rgb = cv2.imread(img_links_rgb_path, cv2.IMREAD_UNCHANGED)
        if img_links_rgb is None:
            raise FileNotFoundError(f"Could not load links RGB layout image at {img_links_rgb_path}")
        
        color_to_mtl = {}
        mtl_defs = []
        material_id = 0
        node_materials = []

        for i in range(int(pfile["nodecount"])):
            y = i % 128
            x = int(i/128)
            npos.append( [(img[x,y][0]*256+imgl[x,y][0])/655.36,(img[x,y][1]*256+imgl[x,y][1])/655.36,(img[x,y][2]*256+imgl[x,y][2])/655.36])
            if "w" in nodes["nodes"][i]:
                nweight.append(ns * nodes["nodes"][i]["w"])
            else:
                nweight.append(ns)

            color = tuple(int(c) for c in img_rgb[x, y])
            if color not in color_to_mtl:
                mtl_name = f"mat_{material_id}"
                color_to_mtl[color] = mtl_name
                mtl_defs.append((mtl_name, color))
                material_id += 1
            node_materials.append(color_to_mtl[color])

        Cverts =[[-0.5, -0.5, -0.5],[-0.5, 0.5, -0.5],[0.5, 0.5, -0.5],[0.5, -0.5, -0.5],[-0.5, -0.5, 0.5],[0.5, -0.5, 0.5],[0.5, 0.5, 0.5],[-0.5, 0.5, 0.5]]
        CUVs=[[0,0],[0.0078125,0],[0.0078125,0.0078125],[0,0.0078125]]
        Ctriangles=[[0,1,2,3],[4,5,6,7],[0,3,5,4],[3,2,6,5],[2,1,7,6],[1,0,4,7]]
        CtrianglesUV=[[0,1,2,3]]*6

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

        linklist = []
        link_materials = []
        for idx, l in enumerate(links["links"]):
            thisl = [l["s"], l["e"]]
            linklist.append(thisl)
            if "w" in l:
                lweight.append(ls * l["w"])
            else:
                lweight.append(ls)

            y = idx % 512
            x = int(idx / 512)
            color = tuple(int(c) for c in img_links_rgb[x, y])
            if color not in color_to_mtl:
                mtl_name = f"mat_{material_id}"
                color_to_mtl[color] = mtl_name
                mtl_defs.append((mtl_name, color))
                material_id += 1
            link_materials.append(color_to_mtl[color])

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
            a = np.array(npos[int(l[0])])
            b = np.array(npos[int(l[1])])
            c = a - b
            p = b + c/2

            k = c/np.linalg.norm(c)
            l = np.linalg.norm(c)
            x = np.random.randn(3)
            x -= x.dot(k) * k / np.linalg.norm(k)**2
            x /= np.linalg.norm(x)
            y = np.cross(k, x)
            m = np.array([k*l,x*scale,y*scale])

            voffset = i * len(Cverts)
            uoffset = i * len(CUVs)
            uv = [i%512, 512 -int(i/512)]
            pos = p

            for v in Cverts:
                vr = np.dot(v,m)
                verts.append([vr[0]+pos[0],vr[1]+pos[1], vr[2]+pos[2]])
            for u in CUVs:
                UVs.append([u[0]/4+uv[0]/512, u[1]*2+uv[1]/64-7.015625])
            for t in Ctriangles:
                Ltriangles.append([t[0]+ voffset + nverts, t[1]+ voffset + nverts, t[2]+ voffset + nverts, t[3]+ voffset + nverts])
            for x in CtrianglesUV:
                LtrianglesUV.append([x[0]+ uoffset + nuv, x[1]+ uoffset + nuv, x[2]+ uoffset + nuv, x[3]+ uoffset + nuv])
            i += 1

        name = "static/projects/"+pname+"/"+ str(count) +".obj"
        mtl_name = str(count) + ".mtl"
        if os.path.isfile(name):
            open(name, 'w').close()
        with open(name, 'a') as f1:
            f1.write(f"mtllib {mtl_name}\n")
            for v in verts:
                f1.write("v " + " ".join(map(str, v)) + '\n')
            for u in UVs:
                f1.write("vt " + " ".join(map(str, u)) + '\n')

            f1.write(f"\ng nodes{count}\n")
            last_mtl = None
            c = 0
            for i in range(nc):
                mtl = node_materials[i]
                if mtl != last_mtl:
                    f1.write(f"usemtl {mtl}\n")
                    last_mtl = mtl
                for _ in range(len(Ctriangles)):
                    t = triangles[c]
                    t_uv = trianglesUV[c]
                    f1.write(f"f {t[0]+1}/{t_uv[0]+1} {t[1]+1}/{t_uv[1]+1} {t[2]+1}/{t_uv[2]+1} {t[3]+1}/{t_uv[3]+1}\n")
                    c += 1

            f1.write(f"\ng links{count}\n")
            last_mtl = None
            c = 0
            for i, t in enumerate(Ltriangles):
                mtl = link_materials[i // len(Ctriangles)]
                if mtl != last_mtl:
                    f1.write(f"usemtl {mtl}\n")
                    last_mtl = mtl
                t_uv = LtrianglesUV[c]
                f1.write(f"f {t[0]+1}/{t_uv[0]+1} {t[1]+1}/{t_uv[1]+1} {t[2]+1}/{t_uv[2]+1} {t[3]+1}/{t_uv[3]+1}\n")
                c += 1

        mtl_path = f"static/projects/{pname}/{mtl_name}"
        with open(mtl_path, 'w') as mtl_file:
            for mtl_name, rgba in mtl_defs:
                r, g, b, a = [v / 255.0 for v in rgba]
                mtl_file.write(f"newmtl {mtl_name}\n")
                mtl_file.write(f"Kd {r:.4f} {g:.4f} {b:.4f}\n")
                mtl_file.write("Ka 0.0000 0.0000 0.0000\n")
                mtl_file.write("Ks 0.0000 0.0000 0.0000\n")
                mtl_file.write(f"d {a:.4f}\n\n")

        count += 1
        print(count)

pfile = {}
pname = "AEscene_MEMES"

with open("static/projects/"+pname+"/pfile.json") as f:
    pfile = json.load(f)

dataDiVR2obj(pfile)
