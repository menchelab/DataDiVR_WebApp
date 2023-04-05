'''
import matplotlib.pyplot as plt                                                                                                                                                               
import numpy as np

x = np.arange(0,100,0.00001)
y = x*np.sin(2*np.pi*x)
plt.plot(y)

'''
"""
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly as plo

plt.rcParams['svg.fonttype'] = 'none'

objects = ('JS','Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
y_pos = np.arange(len(objects))
performance = [70,10,8,6,4,2,1]
 
plt.bar(y_pos, performance, align='center', alpha=0.5, label="reeeeee")
 
plt.xticks(y_pos, objects)
plt.ylabel('Usage')
plt.title('Programming language usage')
 
plt.savefig("test4.svg", format="svg", transparent=True)
plt.show()







fig.show()
fig.write_html('C:/Users/spirch/Desktop/utf-bug.html')
"""
import plotly
import plotly.io as pio
import plotly.graph_objects as go

labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
values = [4500, 2500, 1053, 500]
fig = go.Figure(data=[go.Pie(labels=labels, values=values)])


#fig.show()
script = '<script src="https://cdn.plot.ly/plotly-2.17.1.min.js"></script>'
htmlstring = script + plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

text_file = open("C:/Users/spirch/Desktop/TEST111.html", "w", encoding="utf-8")
text_file.write(htmlstring)
text_file.close()