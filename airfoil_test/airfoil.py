import cadquery as cq

coords = []
with open('airfoil_coordinates.txt', 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) == 2:
            x, y = map(float, parts)
            coords.append((x,y))
        else:
            print('inserire coordinate in 2D')

path = cq.Workplane("XZ").spline(coords).close()
result = path.extrude(2)