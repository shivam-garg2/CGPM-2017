import ezdxf as ez
dwg = ez.readfile("paper_right.dxf")
mdspace = dwg.modelspace()
dwg = ez.readfile("paper_top.dxf")
mdspace_top = dwg.modelspace()
dwg = ez.readfile("paper_front.dxf")
mdspace_1 = dwg.modelspace()
lines_right = mdspace.query('LINE')
lines_top = mdspace_top.query('LINE')
lines_front = mdspace_1.query('LINE')

front_points = []
top_points = []
right_points = []

for line in lines_front:
    front_points += [line.dxf.start, line.dxf.end]
    
for line in lines_top:
    top_points += [line.dxf.start, line.dxf.end]
    
for line in lines_right:
    right_points += [line.dxf.start, line.dxf.end]
    
front_points = set(front_points)
top_points = set(top_points)
right_points = set(right_points)

matches = set()
for point in front_points:
    match_top = set([(point[0], point[1], p[1]) for p in top_points if p[0] == point[0]])
    match_right = set([(point[0], point[1], p[0]) for p in right_points if p[1] == point[1]])
    matches = matches | (match_top & match_right)
for point in top_points:
    match_front = set([(point[0], p[1], point[1]) for p in front_points if p[0] == point[0]])
    match_right = set([(point[0], p[1], point[1]) for p in right_points if p[0] == point[1]])
    matches = matches | (match_front & match_right)
for point in right_points:
    match_top = set([(p[0], point[1], point[0]) for p in top_points if p[1] == point[0]])
    match_front = set([(p[0], point[1], point[0]) for p in right_points if p[1] == point[1]])
    matches = matches | (match_top & match_front)

print matches
