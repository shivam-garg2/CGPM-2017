import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from numpy import *
from numpy import linalg
from math import sqrt
import numpy as np

def normalize(nvector):
	constant = sqrt(nvector[1]**2 + nvector[0]**2 + nvector[2]**2)
	if constant == 0:
		return nvector
	new_vector = (float(nvector[0])/constant, float(nvector[1])/constant, float(nvector[2])/constant)
	if (new_vector[0] < 0) or (new_vector[0] == 0 and new_vector[1] < 0) or (new_vector[0] == 0 and new_vector[1] == 0 and new_vector[2] < 0):
		new_vector = tuple([-1*i for i in new_vector])
	return new_vector

def get_intercept(normal, point):
	return -1*(normal[0]*point[0] + normal[1]*point[1] + normal[2]*point[2])

def cross(v1, v2):
	return (v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])

def subtract(v1, v2):
	return (v1[0] -  v2[0], v1[1] - v2[1], v1[2] - v2[2])


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#input the edges
edges = [[(0, 0, 0), (0, 0, -1)], [(0, 0, -1), (0, 1, -1)], [(0, 1, -1), (0, 1, 0)] , [(0, 1, 0) , (0, 0, -1)] , [(0, 1, -1) , (0,0,0)] ,  [(1, 0, 0), (1, 0, -1)], [(1, 0, -1), (1, 1, -1)], [(1, 1, -1), (1, 1, 0)] , [(1, 1, 0) , (1, 0, -1)] , [(1, 1, -1) , (1, 0, 0)] ,         [(2, 0, 0), (2, 0, -1)], [(2, 0, -1), (2, 1, -1)], [(2, 1, -1), (2, 1, 0)] , [(2, 1, 0) , (2, 0, -1)] , [(2, 1, -1) , (2,0,0)] ,	     [(0, 1, 0) , (1, 1, 0)] , [(1, 1, 0) , (2, 1, 0)] , [(0, 1, -1) , (1, 1, -1)] , [(1, 1, -1) , (2, 1, -1)] , [(0, 0, 0) , (1, 0, 0)] , [(1, 0, 0) , (2, 0, 0)] , [(0, 0, -1) , (1, 0, -1)] , [(1, 0, -1) , (2, 0, -1)]]

n = len(edges)
print n
print(edges)

#plot the edges
X = []
Y = []
Z = []
for t in range(0,n):
	X,Y,Z = [(edges[t][0][0] , edges[t][1][0]) , (edges[t][0][1] , edges[t][1][1]) , (edges[t][0][2] , edges[t][1][2])]
	print X,Y,Z
	ax.scatter(X, Y, Z, zdir='z', s=20, c='g')
	ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)

plt.axis('off')
plt.show()

#extract the individual vertices
vertices = []
for edge in edges:
	vertices += edge
vertices = list(set(vertices))
print vertices
m = len(vertices)
print m

#identify the edges passing through a particular vertice
vertex_edges = {}
for vertex in vertices:
	for edge in edges:
		if vertex in edge:
			vertex_edges[vertex] = vertex_edges.get(vertex, []) + [edge]
print vertex_edges


#Taking out the vertices that form a plane
vertex_diff_vertex = {}
for vertex in vertex_edges.keys():
	edge_vertices = []
	for edge in vertex_edges[vertex]:
		if edge[0] == vertex:
			edge_vertices.append(subtract(edge[1], vertex))
		else:
			edge_vertices.append(subtract(edge[0], vertex))
	vertex_diff_vertex[vertex] = edge_vertices

#Generating the planes
planes = {}
for vertex in vertex_edges.keys():
	for i in range(len(vertex_edges[vertex])):
		for j in range(i+1, len(vertex_edges[vertex])):
			plane_vertices = list(set(vertex_edges[vertex][i] + vertex_edges[vertex][j]))
			normal = normalize(cross(vertex_diff_vertex[vertex][i], vertex_diff_vertex[vertex][j]))
			if normal != (0.0, 0.0, 0.0):
				intercept = get_intercept(normal, vertex)
				plane = tuple(list(normal) + [intercept])
				planes[plane] = list(set(planes.get(plane, []) + plane_vertices))

print 'Break'
print planes

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for key in planes:
	if key[2] == 0:
		if key[1] != 0:
			xx, zz = np.meshgrid(range(0,3), range(-1,1))
			yy = (-key[0]*xx - key[3])/key[1]
		else:
			yy, zz = np.meshgrid(range(0,2), range(-1,1))
			xx = -key[3]/key[0]
	else:
		xx, yy = np.meshgrid(range(0,3), range(0,2))
		zz = (-key[0]*xx - key[1]*yy - key[3])*1 / key[2]

	print zz
	#plt3d = plt.figure().gca(projection='3d')
	ax.plot_surface(xx,yy,zz)



plt.axis('off')
plt.show()


#Identifying Correct 1 Cycle 
points_in_plane  = []
for key in planes: 
	points_in_plane = planes[key]
	print points_in_plane
