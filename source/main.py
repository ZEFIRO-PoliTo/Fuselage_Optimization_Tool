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
    #Taglio il solido conservando solo la parte inferiore al piano           
    .split(keepBottom=True,keepTop=False)
)

#selezione la faccia da cui far partire il loft
faccia_loft = (
    scocca
    .faces('>X')
)

#creo una variabile che contenga il contorno della mia faccia
contorno_loft = faccia_loft.val().outerWire()

result = (
    faccia_loft
    .workplane()                  # Creo un workplane sulla faccia troncata del solido
    .add(contorno_loft)           #aggiungo il perimetro della faccia al workplane
    .toPending()                  # Indico che questo perimetro è il primo da usare per il loft
    
    .workplane(offset=500)        # Creo il secondo piano parallelo
    .moveTo(0,-150).circle(200)   # Secondo profilo guida del loft
    .loft(combine=True)
)

show_object(result)
