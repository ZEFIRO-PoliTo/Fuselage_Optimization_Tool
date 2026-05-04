import cadquery as cq

percorso_file = 'Airspeeder_Mk3_proxy_simplified.step'
x_taglio = 1300.0 
#credo prenda come 0 dell'asse x il centro del solido
# ma non ho ancora ben cpito il perchè 

scocca = (
    cq.importers.importStep(percorso_file)
    # rotazione di 90° su asse X
    .rotate((0,0,0), (1,0,0), 90)
    # rotazione di 90° su asse Z
    .rotate((0,0,0), (0,0,1), 90)
) 

result = (
    cq.Workplane('YZ')
    .add(scocca.solids().vals())
    .workplane(offset=x_taglio)
    .split(keepBottom=True,keepTop=False)
)


show_object(result)

