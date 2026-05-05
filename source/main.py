import cadquery as cq

percorso_file = 'Airspeeder_Mk3_proxy_simplified.step'   #importo il file STEP da Solidworks
x_taglio = 1300.0 
#credo prenda come 0 dell'asse x il centro del solido
# ma non ho ancora ben cpito il perchè 

scocca = (
    cq.importers.importStep(percorso_file)    
    .rotate((0,0,0), (1,0,0), 90)   # rotazione di 90° su asse X 
    .rotate((0,0,0), (0,0,1), 90)   # rotazione di 90° su asse Z
) 

result = (
    cq.Workplane('YZ')
    .add(scocca.solids().vals())              #aggiunge il solido inportato al piano di lavoro
    .workplane(offset=x_taglio)               #crea il piano di taglio
    .split(keepBottom=True,keepTop=False)     #taglia la parte superiore al piano
)

show_object(result)
