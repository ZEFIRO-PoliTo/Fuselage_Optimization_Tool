import cadquery as cq

# caratteristiche del cono centrale del propulsore
raggio_base = 6.0
raggio_cima = 5.0
altezza_tot = 15.0
altezza_punta = 8.0
angolo_punta = 0 # ancora da implementare

# caratteristiche pala del proulsore
coeff_x = 8.0  # coefficiente di ingrandimento
coeff_y = 15
lunghezza_blade = 20.0
twist_blade = 20.0    # angolo di inclinazione all'estremo della pala
numero_blades = 4


# lista dei punti che compongono il profilo alare 
# partendo dalla faccia superiore del trailg edge
coords = [] 
offset_x = -coeff_x/2         # sono le coordinate che usermo per centrale le pale
offset_y = altezza_punta/2

with open('data/airfoil_coordinates.txt', 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) == 2:
            x, y = map(float, parts)
            coords.append((coeff_x*x + offset_x, coeff_y*y + offset_y))
        else:
            print('inserire coordinate in 2D')

propeller_nose = (
    cq.Workplane("XZ")
    .polyline([(0,0), (raggio_base,0), (raggio_cima,altezza_punta)])
    .spline([(raggio_cima,altezza_punta),(0,altezza_tot)], 
            tangents=[(raggio_cima-raggio_base, altezza_punta),(-1,0.6)]) 
    .lineTo(0,0)
    .close()
    .revolve(360.0, (0,0), (0,1))
   )

blade = (
    cq.Workplane("XZ")
    .spline(coords)      # crea il profilo alare dalle cordinate nella lista coords 
    .close()
    .twistExtrude(lunghezza_blade,-twist_blade)
    )



total_blade = cq.Workplane("XZ") 

for i in range(numero_blades):
    angolo = i * (360.0/numero_blades)
    copia_ruotata = blade.rotate((0,0,0), (0,0,1), angolo)
    total_blade = total_blade.union(copia_ruotata)

result = propeller_nose.union(total_blade)
