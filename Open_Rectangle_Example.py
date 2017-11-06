import ezdxf as ez
from axes3d import axes3d as pls
dwg = ez.readfile("Part2_Dotted.dxf")
mdspace = dwg.modelspace()
lines = mdspace.query('LINE')
points = []
for line in lines:
	points += [line.dxf.start, line.dxf.end]

points = list(set(points))
print points
print len(points)
for i in points:
        print i


dwg2 = ez.readfile("Paper_Isometric.dxf")
mdspace2 = dwg.modelspace()
lines2 = mdspace.query('LINE')
points2 = []
for line in lines2:
	points2 += [line.dxf.start, line.dxf.end]

points2 = list(set(points2))
print points2
print len(points2)
for i in points2:
        print i
"""
edges = [[(0,0,0),(0,50,0)],[(100,50,0),(0,50,0)],[(100,50,0),(100,0,0)],[(100,0,0),(0,0,0)]]
pls(edges)
"""


from operator import itemgetter
a,b,c = map(itemgetter(0),points), map(itemgetter(1),points),map(itemgetter(2),points)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(a,b,c, zdir='c' , s=20, c='g')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
#plt.plot(a,b,c,'ro')

plt.axis('off')
plt.show()
