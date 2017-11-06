import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from numpy import *
from numpy import linalg
from math import sqrt

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

edges = [[(0, 0, 0), (0, 0, -1)], [(0, 0, -1), (0, 1, -1)], [(0, 1, -1), (0, 1, 0)] , [(0, 1, 0) , (0, 0, -1)] , [(0, 1, -1) , (0,0,0)] ,  [(1, 0, 0), (1, 0, -1)], [(1, 0, -1), (1, 1, -1)], [(1, 1, -1), (1, 1, 0)] , [(1, 1, 0) , (1, 0, -1)] , [(1, 1, -1) , (1, 0, 0)] ,         [(2, 0, 0), (2, 0, -1)], [(2, 0, -1), (2, 1, -1)], [(2, 1, -1), (2, 1, 0)] , [(2, 1, 0) , (2, 0, -1)] , [(2, 1, -1) , (2,0,0)] ,	     [(0, 1, 0) , (1, 1, 0)] , [(1, 1, 0) , (2, 1, 0)] , [(0, 1, -1) , (1, 1, -1)] , [(1, 1, -1) , (2, 1, -1)] , [(0, 0, 0) , (1, 0, 0)] , [(1, 0, 0) , (2, 0, 0)] , [(0, 0, -1) , (1, 0, -1)] , [(1, 0, -1) , (2, 0, -1)]]

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

vertex_diff_vertex = {}

for vertex in vertex_edges.keys():
	edge_vertices = []
	for edge in vertex_edges[vertex]:
		if edge[0] == vertex:
			edge_vertices.append(subtract(edge[1], vertex))
		else:
			edge_vertices.append(subtract(edge[0], vertex))
	vertex_diff_vertex[vertex] = edge_vertices

planes = {}
for vertex in vertex_edges.keys():
	for i in range(len(vertex_edges[vertex])):
		for j in range(i+1, len(vertex_edges[vertex])):
			plane_vertices = list(set(vertex_edges[vertex][i] + vertex_edges[vertex][j]))
			normal = normalize(cross(vertex_diff_vertex[vertex][i], vertex_diff_vertex[vertex][j]))
			if normal != (0.0, 0.0, 0.0):
				intercept = get_intercept(normal, vertex)
				plane = tuple(list(normal) + [intercept])
				if plane not in planes.keys():
					planes[plane] = plane_vertices
print "PLAAAAANES"
print planes