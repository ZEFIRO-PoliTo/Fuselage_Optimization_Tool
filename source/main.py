import cadquery as cq

percorso_file = 'Airspeeder_Mk3_proxy_simplified.step'
x_taglio = 1300.0 
#credo prenda come 0 dell'asse x il centro del solido
# ma non ho ancora ben cpito il perchè 

corpo_importato = (
    cq.importers.importStep(percorso_file)
    # Rotazione di 90° su asse X
    .rotate((0,0,0), (1,0,0), 90)
    # Rotazione di 90° su asse Z
    .rotate((0,0,0), (0,0,1), 90)
) 

scocca = (
    cq.Workplane('YZ')
    # Aggiungo il mio corpo importato al workplane
    # I comandi .solids() e .vals() si assicurano che CadQuery lo registri come un solido
    .add(corpo_importato.solids().vals()) 
    # Creo un piano di lavoro dove voglio effettuare il taglio
    .workplane(offset=x_taglio)  
    # Taglio il solido conservando solo la parte inferiore al piano           
    .split(keepBottom=True,keepTop=False)
)

# Selezione la faccia da cui far partire il loft
faccia_loft = (
    scocca
    .faces('>X')
)

# Creo una variabile che contenga il contorno della mia faccia
contorno_loft = faccia_loft.val().outerWire()

offset_z = -135       # Serve a centrare i cerchi per creare il loft

# Caratteristiche del cono di punta
raggio_base = 220.0
raggio_cima = 150.0
altezza_tot = 250.0
altezza_punta = 140.0
angolo_punta = 0 # Ancora da implementare
loft = (
    faccia_loft
    .workplane()                  # Creo un workplane sulla faccia troncata del solido
    .add(contorno_loft)           #aggiungo il perimetro della faccia al workplane
    .toPending()                  # Indico che questo perimetro è il primo da usare per il loft
    
    .workplane(offset=120)        # Creo il secondo piano parallelo
    .moveTo(0,offset_z)           # Serve a centrare il cerchio lungo z
     # Sarebbe bello trovare un modo per centrarlo indipendentemente dall'oggetto
    .circle(raggio_base)                  # Secondo profilo guida del loft

    .loft(combine=True)
)

# Mi ricavo le coordinate del centro del cerchio da cui far partire il cono di punta
centro_punta = (
    loft
    .faces('>X')
    .val()
    .Center()
)

propeller_nose = (
    cq.Workplane("XZ")    # Disegno il profilo del cono di punta
    # Sposto l'origine del mio workplane al centro del cerchio
    .center(centro_punta.x, centro_punta.z) 
    .polyline([(0, 0),   
               (0, raggio_base), 
               (altezza_punta, raggio_cima)])
    .spline([(altezza_punta, raggio_cima),
             (altezza_tot, 0)], 
            tangents=[(altezza_punta, raggio_cima-raggio_base),
                      (-1,0.6)])  # Da qui posso modificare la tangenza sulla punta
    .lineTo(0, 0)
    .close()
    .revolve(360.0, (0,0), (1, 0))    # Faccio ruotare intorno all'asse X
   )
   
result = loft.union(propeller_nose)
show_object(result)
