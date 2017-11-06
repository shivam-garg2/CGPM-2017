import functions
from functions import *

if __name__ == '__main__':
	front_view = 'Diamond_front.dxf'
	back_view = 'Diamond_back.dxf'
	top_view = 'Diamond_top.dxf'
	bottom_view = 'Diamond_bottom.dxf'
	left_view = 'Diamond_left.dxf'
	right_view = 'Diamond_right.dxf'
	projections = {}
	projections['XY'] = edge_breakdown(get_view(top_view, bottom_view))
	projections['XZ'] = edge_breakdown(get_view(front_view, back_view))
	projections['YZ'] = edge_breakdown(get_view(right_view, left_view))
	a,b = generate_pseudo_wireframe(projections)
	axes3d(a)
	print b
	get_planes_and_faces(a, b)
