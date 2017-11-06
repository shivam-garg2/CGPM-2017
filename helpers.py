import ezdxf as ez
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import sqrt
import numpy as np

class Node(object):
	def __init__(self, value, parent = None):
		self.value = value
		self.parent = parent
	
	def traverse_ancestors(self):
		pointer = self
		while pointer.parent != None:
			pointer = pointer.parent
			if pointer.value == self.value:
				if pointer.parent == None:
					return 2
				else:
					return 1
		return 0

	def get_face(self):
		pointer = self
		face = []
		while pointer.parent != None:
			face.append(pointer.value)
			pointer = pointer.parent
		return tuple(face)

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

def is_vertex_on_edge_2D(vertex, line):
	epsilon = 1e-4
	v1 = line[0]
	v2 = line[-1]
	if vertex[0] != v2[0]:
		lam = float(v1[0] - v2[0])/(vertex[0] - v2[0])
		if lam > 1:
			if abs(v1[1] - v2[1] - lam*(vertex[1] - v2[1])) < epsilon:
				return True
	elif vertex[0] == v2[0] and vertex[0] == v1[0]:
		y_low, y_high = sorted([v1[1], v2[1]])
		if y_low < vertex[1] < y_high:
			return True
	return False

def is_p_edge(v1, v2, projection):
	if v1 == v2:
		if (v1 in projection['Vertices']) or is_vertex_internal(v1, projection['Lines']):
			return 1
	else:
		for line in projection['Lines']:
			if (v1 in line or is_vertex_on_edge_2D(v1, line)) and (v2 in line or is_vertex_on_edge_2D(v2, line)):
				return 2
	return 0

def is_vertex_internal(vertex, lines):
	result = False
	for line in lines:
		if is_vertex_on_edge_2D(vertex, line):
			result = True
			break
	return result

def edges_intersect_3D(edge1, edge2):
	V_00 = np.reshape(np.array(edge1[0]), (-1,1))
	V_01 = np.reshape(np.array(edge1[1]), (-1,1))
	V_10 = np.reshape(np.array(edge2[0]), (-1,1))
	V_11 = np.reshape(np.array(edge2[1]), (-1,1))
	A = np.hstack((V_11-V_10, V_00-V_01))
	b = V_00 - V_10
	x, residuals, _, _ = np.linalg.lstsq(A, b)
	if residuals == [0]:
		if np.all(np.logical_and(x > 0, x < 1)):
			print x, residuals
			return tuple((V_10 + (V_11 - V_10)*x[0]).flatten())
	return None

def axes3d(edges):

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	n = len(edges)
#	print n

#	print(edges)

	X = []
	Y = []
	Z = []

	for t in range(0,n):
		X,Y,Z = [(edges[t][0][0] , edges[t][1][0]) , (edges[t][0][1] , edges[t][1][1]) , (edges[t][0][2] , edges[t][1][2])]
#		print X,Y,Z
		ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
	
	plt.axis('off')	
	plt.show()
