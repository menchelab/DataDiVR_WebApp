import json
import csv




# Opening JSON file
f = open('custom.geo.json' ,encoding='utf-8')
data = json.load(f)

polygons=[]
pointsum=0
count = 0
for i in data['features']:
    if count < 1000:

        #print (i["properties"]["name_ciawf"])
        #print(i["geometry"]["type"])
        
        if (i["geometry"]["type"] == "Polygon"):
            for p in i["geometry"]["coordinates"]:
                #print(i["geometry"])
                polygons.append(p)
                pointsum=pointsum+len(p)
           
        if (i["geometry"]["type"] == "MultiPolygon"):
            for p in i["geometry"]["coordinates"]:
                for x in p:
                    polygons.append(x)
                    pointsum=pointsum+len(x)
         
    count += 1

print(polygons)
print(pointsum)
with open('borders_geo1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for poly in polygons:
        for point in poly:
            writer.writerow([point[1],point[0]])

with open('borders_edges.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    p = 0
    for poly in polygons:
        for x in range(len(poly)):
            if x < (len(poly)- 1): 
                writer.writerow([p,p+1])
            p += 1


