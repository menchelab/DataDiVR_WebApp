import uploaderNew
import random
import pandas as pd
import socketio

#df = pd.read_excel("ExampleSpectroscopyData.xlsx", header=3)


dim = [1447,1447]

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
colors = [[255,0,0,128],[0,255,0,128],[0,0,255,128],[255,255,0,128],[0,128,255,128],[128,0,255,128],[0,0,255,128],[255,255,0,128]]
count = 0
for u in range(0,dim[1]):
#u = 100
    for i in range (0,dim[0]+1):
        thisnode = {"id": i + u*dim[0], "name": "node_"+ str(i + u*dim[0]), "special":"someotherproject"}
        nodelist.append(thisnode)

        zpos = 0.15
        nodepos.append([(u/dim[1]),(i/dim[0]), zpos])
        #
        #if i < 10:
            #print(df[i,3])
        #nodecol.append([zpos * 255,zpos * 255,50, 130 + zpos * 30])
        nodecol.append([255,zpos * 255,50, 130 + zpos * 30])

        if i > 0 :

            linklist.append([count, count-1])
            
            #
            linkcol.append(colors[int(((u-1)/64)%8)])
        #if u > 0:
            #linklist.append([u + i*dim[1], u-1 + i*dim[1]])
            #linkcol.append([250,0,0,255])
        count += 1
print("links:"+ str(len(linklist)))
projectname = str(dim[0])+"x"+str(dim[1])

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