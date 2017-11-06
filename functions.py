import helpers
from helpers import *

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

def generate_pseudo_wireframe(projections):
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
	candidate_edges_temp = []
	for i in range(len(candidate_vertex_list)):
		for j in range(i+1, len(candidate_vertex_list)):
			vertex_i = candidate_vertex_list[i]
			vertex_j = candidate_vertex_list[j]
			xy = lambda v: (v[0],v[1])
			yz = lambda v: (v[1],v[2])
			xz = lambda v: (v[0],v[2])
			status = [is_p_edge(xy(vertex_i), xy(vertex_j), projections['XY']), is_p_edge(yz(vertex_i), yz(vertex_j), projections['YZ']), is_p_edge(xz(vertex_i), xz(vertex_j), projections['XZ'])]
			if status == [2,2,2] or sorted(status) == [1,2,2]:
				candidate_edges_temp.append((vertex_i, vertex_j))
	candidate_edges = []
	for i in range(len(candidate_edges_temp)):
		intermediate_vertices = []
		for j in range(len(candidate_edges_temp)):
			if j != i:
				x = edges_intersect_3D(candidate_edges_temp[i], candidate_edges_temp[j])
				if x is not None:
					intermediate_vertices.append(x)
		vertices = tuple(sorted(sorted(sorted(intermediate_vertices + list(candidate_edges_temp[i]), key = lambda v: v[2]), key = lambda v: v[1]), key = lambda v: v[0]))
		for k in range(len(vertices)-1):
			candidate_edges.append((vertices[k], vertices[k+1]))
	return candidate_edges, candidate_vertex_list

def get_planes_and_faces(edges, vertices):
	for i in range(len(edges)):
		edges[i] = tuple(sorted(sorted(sorted(edges[i], key = lambda v: v[2]), key = lambda v: v[1]), key = lambda v: v[0]))

	#extract the individual vertices
	#vertices = []
	#for edge in edges:
	#	vertices += edge
	#vertices = list(set(vertices))

	#identify the edges passing through a particular vertice
	vertex_edges = {}
	for vertex in vertices:
		for edge in edges:
			if vertex in edge:
				vertex_edges[vertex] = vertex_edges.get(vertex, []) + [edge]

	#Taking out the vectors that form a plane and neighbouring vertices to vertex
	vertex_diff_vertex = {}
	vertex_vertex = {}
	for vertex in vertex_edges.keys():
		edge_vertices = []
		vertex_neighbours = []
		for edge in vertex_edges[vertex]:
			if edge[0] == vertex:
				vertex_neighbours.append(edge[1])
				edge_vertices.append(subtract(edge[1], vertex))
			else:
				vertex_neighbours.append(edge[0])
				edge_vertices.append(subtract(edge[0], vertex))
		vertex_diff_vertex[vertex] = edge_vertices
		vertex_vertex[vertex] = vertex_neighbours

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

	#fig = plt.figure()
	#ax = fig.add_subplot(111, projection='3d')
	
	for key in planes:
		x_sort = sorted(planes[key], key = lambda v: v[0])
		y_sort = sorted(planes[key], key = lambda v: v[1])
		z_sort = sorted(planes[key], key = lambda v: v[2])
		x_min = int(x_sort[0][0]); x_max = int(x_sort[-1][0]) + 1
		y_min = int(y_sort[0][1]); y_max = int(y_sort[-1][1]) + 1
		z_min = int(z_sort[0][2]); z_max = int(z_sort[-1][2]) + 1
		if key[2] == 0:
			if key[1] != 0:
				xx, zz = np.meshgrid(range(x_min, x_max), range(z_min, z_max))
				yy = (-key[0]*xx - key[3])/key[1]
			else:
				yy, zz = np.meshgrid(range(y_min, y_max), range(z_min, z_max))
				xx = -key[3]/key[0]
		else:
			xx, yy = np.meshgrid(range(x_min, x_max), range(y_min, y_max))
			zz = (-key[0]*xx - key[1]*yy - key[3])*1 / key[2]

		#plt3d = plt.figure().gca(projection='3d')
		#ax.plot_surface(xx,yy,zz)

	#plt.axis('off')
	#plt.show()

	#Identifying Correct 1 Cycle 
	cycles = []
	for plane in planes: 
		points_in_plane = planes[plane]
		#edge_buffer = []
		#for vertex in points_in_plane:
		#	for edge in vertex_edges[vertex]:
		#		if edge[0] in points_in_plane and edge[1] in points_in_plane and edge not in edge_buffer:
		#			edge_buffer.append(edge)
		#print edge_buffer
		#while len(edge_buffer) > 0:
		#	found_face = False
		leaves = []
		root_v = points_in_plane[0]
		root = Node(root_v)
		queue = [Node(vertex, root) for vertex in vertex_vertex[root.value] if vertex in points_in_plane]
		for node in queue:
			is_loop = node.traverse_ancestors()
			if is_loop > 0:
				leaves.append(node)
				continue
			#elif is_loop == 2:
				#face = node.get_face()
				#for i in range(len(face)-1):
				#	edge = tuple(sorted(sorted(sorted((face[i], face[i+1]), key = lambda v: v[2]), key = lambda v: v[1]), key = lambda v: v[0]))
				#	if edge in edge_buffer:
				#		edge_buffer.remove(edge)
				#faces.append(face)
				#found_face = True
				#break
			queue.extend([Node(vertex, node) for vertex in vertex_vertex[tuple([round(i,5) for i in node.value])] if (vertex != node.parent.value and vertex in points_in_plane)])
		for leaf in leaves:
			cycle = leaf.get_face()
			print cycle
			cycles.append(cycle)

