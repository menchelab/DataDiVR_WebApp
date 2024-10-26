import uploaderNew
import random
import pandas as pd
import socketio

df = pd.read_excel("ExampleSpectroscopyData.xlsx", header=3)
df.index
#print(df)

df = df.iloc[1:,1:]
df = df.values
df = df[::1,::1]
#[ spectrum, time]
#print(df.columns)
#print(df[4,1])
#print(df[:,1])
#print(df)

dim = df.shape

'''
nodelist = [{"id":356, "name":"heinz"},{"id":234, "name":"karl"},{"id":899, "name":"eric"},{"id":899, "name":"anton"}]
linklist = [[0,1],[0,2],[0,3]]
nodepos = [[0,0,0],[0,0,1],[1,0,0],[0,1,0]]
nodecol = [[255,0,0,255],[255,255,0,255],[0,255,0,255],[0,0,255,255]]
linkcol = [[255,0,0,255],[255,255,0,255],[0,255,0,255]]
'''
nodelist = []
linklist = []
nodepos = []
nodecol = []
linkcol = []

labels = [{"id":12,"n":"X","group":[3]},{"id":12,"n":"Y","group":[1]},{"id":12,"n":"Z","group":[2]}]
ugs = 0
print(df.shape)
for u in range(dim[1]):
#u = 100
    for i in range (dim[0]):
        thisnode = {"id": i + u*dim[0], "name": "node_"+ str(i + u*dim[0])}
        nodelist.append(thisnode)

        zpos = (df[i,u])/100000
        nodepos.append([(u/dim[1]),(i/dim[0]), zpos])
        #
        #if i < 10:
            #print(df[i,3])
        #nodecol.append([zpos * 255,zpos * 255,50, 130 + zpos * 30])
        nodecol.append([255,zpos * 255,50, 130 + zpos * 30])

        if i > 0 :

            linklist.append([i + u*dim[0], i-1 + u*dim[0]])
         
            linkcol.append([random.randint(128,255),random.randint(128,255),random.randint(128,255),255])

projectname = "r54XX12"

uploaderNew.makeProjectFolders(projectname)

uploaderNew.makeNodeTex(projectname, "test1", nodelist , labels, nodepos, nodecol)
for i in range (len(nodecol)):
    nodecol[i] = [nodepos[i][0]*255,nodepos[i][1]*255,nodepos[i][2]*500,100]
uploaderNew.makeNodeTex(projectname, "test2", nodelist , labels, nodepos, nodecol)

uploaderNew.makeLinkTex(projectname, "test1", linklist, linkcol)


#uploaderNew.update_files("testname", nodelist, linklist, nodepos, nodecol, linklist, linkcol)
uploaderNew.updatePfile(projectname, nodelist,labels, linklist)

# FINISHED - NOTIFY SERVER

sio = socketio.Client()
sio.connect('http://localhost:5000', namespaces=['/main'])
sio.emit('ex', {'id': 'client', "usr":"reee", "fn":"refresh"}, namespace='/main' )


@sio.on('ex', namespace='/main')
def response(data):
    print(data)  # {'from': 'server'}

    sio.disconnect()
    exit(0)