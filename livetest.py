import uploaderNew
import random
import pandas as pd


df = pd.read_excel("ExampleSpectroscopyData.xlsx", header=3)
df.index
#print(df)

df = df.iloc[1:,:]
df = df.values
df = df[::2,::2]
#print(df.columns)
#print(df.values[0,1])
#print(df[:,1])
#print(df)

dim = df.shape


nodelist = [{"id":356, "name":"heinz"},{"id":234, "name":"karl"},{"id":899, "name":"eric"}]
linklist = [[0,1],[1,2],[0,2]]
nodepos = [[0,0,0],[-0.1,0.2,0.4],[0.3,-0.2,-0.4]]
nodecol = [[255,0,0,255],[255,255,0,255],[0,255,0,255]]
linkcol = [[255,0,0,255],[255,255,0,255],[0,255,0,255]]

for u in range(df.shape[0]-1):
    for i in range (df.shape[1]-1):
        thisnode = {"id": i, "name": "node_"+ str(i)}
        nodelist.append(thisnode)
        nodepos.append([u/dim[0],(i/dim[0]), ((df[u,i])/100000)+0.05])
        nodecol.append([random.randint(50,255),random.randint(50,255),random.randint(50,255),255])

for i in range (100):
    linklist.append([random.randint(0, 10000),0])
    linkcol.append([random.randint(0,255),random.randint(0,255),random.randint(0,255),255])

projectname = "r54XX12"

uploaderNew.makeProjectFolders(projectname)

uploaderNew.makeNodeTex(projectname, "test1", nodelist, nodepos, nodecol)

uploaderNew.makeLinkTex(projectname, "test1", linklist, linkcol)


#uploaderNew.update_files("testname", nodelist, linklist, nodepos, nodecol, linklist, linkcol)
uploaderNew.updatePfile(projectname, nodelist, linklist)

# %%
