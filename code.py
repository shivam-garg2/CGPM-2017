import ezdxf as ez
from axes3d import axes3d
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def get_EV(filename, invert = False):
	dwg = ez.readfile(filename)
	modelspace = dwg.modelspace()
	lines = modelspace.query('LINE')
	edges = []
	vertices = []
	for line in lines:
		edges.append((line.dxf.start[0:2], line.dxf.end[0:2]))
		vertices += [line.dxf.start[0:2], line.dxf.end[0:2]]
	vertices = list(set(vertices))
	if invert:
		edges = [((abs(e[0][0]), abs(e[0][1])),(abs(e[1][0]), abs(e[1][1]))) for e in edges]
		vertices = [(abs(v[0]), abs(v[1])) for v in vertices]
	return edges, vertices

def get_view(view_1, view_2):
	e1, v1 = get_EV(view_1)
	e2, v2 = get_EV(view_2, invert = True)
	vertices = list(set(v1+v2))
	edges = e1[:]
	for an_edge in e2:
		flag = False
		for another_edge in e1:
			if (an_edge == another_edge or an_edge == another_edge[::-1]):
				flag = True
		if not flag:
			edges.append(an_edge)
	for i in range(len(edges)):
		edges[i] = tuple(sorted(sorted(edges[i], key = lambda v: v[1]), key = lambda v: v[0]))
	return {'Edges': edges, 'Vertices': vertices}

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

def is_vertex_internal(vertex, lines):
	result = False
	for line in lines:
		if is_vertex_on_edge_2D(vertex, line):
			result = True
			break
	return result

def edge_breakdown(projection):
	edges = projection['Edges']
	vertices = projection['Vertices']
	lines = []
	new_edges = []
	for edge in edges:
		x_low, x_high = tuple(sorted([point[0] for point in edge]))
		y_low, y_high = tuple(sorted([point[1] for point in edge]))
		possible_inters = []
		for vertex in vertices:
			if x_low < vertex[0] < x_high and y_low <= vertex[1] <= y_high:
				possible_inters.append(vertex)
			elif x_low <= vertex[0] <= x_high and y_low < vertex[1] < y_high:
				possible_inters.append(vertex)
		intermediate_vertices = sorted([vertex for vertex in possible_inters if is_vertex_on_edge_2D(vertex, edge)], key = lambda x: x[0])
		if len(intermediate_vertices) > 0:
			if edge[0][0] > edge[1][0]:
				intermediate_vertices = intermediate_vertices[::-1]
			start = edge[0]
			end = edge[1]
			line = [start] + intermediate_vertices + [end]
			line = tuple(sorted(sorted(line, key = lambda v: v[1]), key = lambda v: v[0]))
			if line not in lines:
				lines.append(line)
			for i in range(len(line)-1):
				new_edges.append((line[i], line[i+1]))
		else:
			new_edges.append(edge)
			lines.append(edge)
	return {'Edges' : new_edges, 'Vertices' : vertices, 'Lines': lines}

def is_p_edge(v1, v2, projection):
	if v1 == v2:
		if (v1 in projection['Vertices']) or is_vertex_internal(v1, projection['Lines']):
			return 1
	else:
		for line in projection['Lines']:
			if (v1 in line or is_vertex_on_edge_2D(v1, line)) and (v2 in line or is_vertex_on_edge_2D(v2, line)):
				return 2
	return 0

def generate_pseudo_skeleton(projections):
	candidate_vertices = {}
	proj_vertex_freqs = {}
	for key in projections.keys():
		proj_vertex_freqs[key] = {k: [] for k in projections[key]['Vertices']}
	#Finding all Candidate Vertices
	for vertex_xz in proj_vertex_freqs['XZ'].keys():
		for vertex_yz in proj_vertex_freqs['YZ'].keys():
			if vertex_xz[1] == vertex_yz[1]:
				candidate_vertex = (vertex_xz[0], vertex_yz[0], vertex_xz[1])
				if candidate_vertex not in candidate_vertices.keys():
					candidate_vertices[candidate_vertex] = {'XY' : None, 'YZ': vertex_yz, 'XZ': vertex_xz}
					proj_vertex_freqs['YZ'][vertex_yz].append(candidate_vertex)
					proj_vertex_freqs['XZ'][vertex_xz].append(candidate_vertex)
					if (vertex_xz[0], vertex_yz[0]) in proj_vertex_freqs['XY'].keys():
						candidate_vertices[candidate_vertex]['XY'] = (vertex_xz[0], vertex_yz[0])
						proj_vertex_freqs['XY'][(vertex_xz[0], vertex_yz[0])].append(candidate_vertex)
					elif not is_vertex_internal((vertex_xz[0], vertex_yz[0]), projections['XY']['Lines']):
						candidate_vertices.pop(candidate_vertex)
						proj_vertex_freqs['YZ'][vertex_yz].pop()
						proj_vertex_freqs['XZ'][vertex_xz].pop()

	for vertex_xz in proj_vertex_freqs['XZ'].keys():
		for vertex_xy in proj_vertex_freqs['XY'].keys():
			if vertex_xz[0] == vertex_xy[0]:
				candidate_vertex = (vertex_xz[0], vertex_xy[1], vertex_xz[1])
				if candidate_vertex not in candidate_vertices.keys():
					candidate_vertices[candidate_vertex] = {'XY' : vertex_xy, 'YZ': None, 'XZ': vertex_xz}
					proj_vertex_freqs['XY'][vertex_xy].append(candidate_vertex)
					proj_vertex_freqs['XZ'][vertex_xz].append(candidate_vertex)
					if (vertex_xy[1], vertex_xz[1]) in proj_vertex_freqs['YZ'].keys():
						candidate_vertices[candidate_vertex]['YZ'] = (vertex_xy[1], vertex_xz[1])
						proj_vertex_freqs['YZ'][(vertex_xy[1], vertex_xz[1])].append(candidate_vertex)
					elif not is_vertex_internal((vertex_xy[1], vertex_xz[1]), projections['YZ']['Lines']):
						candidate_vertices.pop(candidate_vertex)
						proj_vertex_freqs['XY'][vertex_xy].pop()
						proj_vertex_freqs['XZ'][vertex_xz].pop()
					
	for vertex_xy in proj_vertex_freqs['XY'].keys():
		for vertex_yz in proj_vertex_freqs['YZ'].keys():
			if vertex_xy[1] == vertex_yz[0]:
				candidate_vertex = (vertex_xy[0], vertex_yz[0], vertex_yz[1])
				if candidate_vertex == (50.0, 35.0, 0.0):
					import pdb; pdb.set_trace()
				if candidate_vertex not in candidate_vertices.keys():
					candidate_vertices[candidate_vertex] = {'XY' : vertex_xy, 'YZ': vertex_yz, 'XZ': None}
					proj_vertex_freqs['YZ'][vertex_yz].append(candidate_vertex)
					proj_vertex_freqs['XY'][vertex_xy].append(candidate_vertex)
					if (vertex_xy[0], vertex_yz[1]) in proj_vertex_freqs['XZ'].keys():
						candidate_vertices[candidate_vertex]['XZ'] = (vertex_xy[0], vertex_yz[1])
						proj_vertex_freqs['XZ'][(vertex_xy[0], vertex_yz[1])].append(candidate_vertex)
					elif not is_vertex_internal((vertex_xy[0], vertex_yz[1]), projections['XZ']['Lines']):
						candidate_vertices.pop(candidate_vertex)
						proj_vertex_freqs['YZ'][vertex_yz].pop()
						proj_vertex_freqs['XY'][vertex_xy].pop()
	
	#Marking Candidate Vertices
	for vertex in candidate_vertices.keys():
		candidate_vertices[vertex]['type'] = 'uncertain'
	consolidated_P_vertices = {}
	for key in proj_vertex_freqs.keys():
		consolidated_P_vertices.update(proj_vertex_freqs[key])
	for p_vertex in consolidated_P_vertices.keys():
		if len(consolidated_P_vertices[p_vertex]) == 1:
			candidate_vertices[consolidated_P_vertices[p_vertex][0]]['type'] = 'certain'

	for key in proj_vertex_freqs.keys():
		for vertex in proj_vertex_freqs[key].keys():
			if len(proj_vertex_freqs[key][vertex]) == 0:
				proj_vertex_freqs[key].pop(vertex)
				projections[key]['Vertices'].remove(vertex)
				projections[key]['Edges'] = [edge for edge in projections[key]['Edges'] if vertex not in edge]

	#Get skeletal edges
	candidate_vertex_list = candidate_vertices.keys()
	candidate_edges = []
	for i in range(len(candidate_vertex_list)):
		for j in range(i+1, len(candidate_vertex_list)):
			vertex_i = candidate_vertex_list[i]
			vertex_j = candidate_vertex_list[j]
			xy = lambda v: (v[0],v[1])
			yz = lambda v: (v[1],v[2])
			xz = lambda v: (v[0],v[2])
			status = [is_p_edge(xy(vertex_i), xy(vertex_j), projections['XY']), is_p_edge(yz(vertex_i), yz(vertex_j), projections['YZ']), is_p_edge(xz(vertex_i), xz(vertex_j), projections['XZ'])]
			if status == [2,2,2] or sorted(status) == [1,2,2]:
				candidate_edges.append((vertex_i, vertex_j))
	return candidate_edges, candidate_vertex_list

if __name__ == '__main__':
	front_view = 'paper_front.dxf'
	back_view = 'paper_back.dxf'
	top_view = 'paper_top.dxf'
	bottom_view = 'paper_bottom.dxf'
	left_view = 'paper_left.dxf'
	right_view = 'paper_right.dxf'
	projections = {}
	projections['XY'] = edge_breakdown(get_view(top_view, bottom_view))
	projections['XZ'] = edge_breakdown(get_view(front_view, back_view))
	projections['YZ'] = edge_breakdown(get_view(right_view, left_view))
	a,b = generate_pseudo_skeleton(projections)
	axes3d(a)
	print b
