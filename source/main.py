import cadquery as cq
from cadquery import Face, Wire
from cadquery.occ_impl.shapes import Edge
import math

percorso_file = 'Airspeeder_Mk3_proxy_simplified.step'
variazione_sezioni=100                    #distanza tra le due sezioni
x_taglio = 1300.0-variazione_sezioni
x_taglio2 = x_taglio+variazione_sezioni
#credo prenda come 0 dell'asse x il centro del solido
# ma non ho ancora ben cpito il perchè 

corpo_importato = (
    cq.importers.importStep(percorso_file)
    # Rotazione di 90° su asse X
    .rotate((0,0,0), (1,0,0), 90)
    # Rotazione di 90° su asse Z
    .rotate((0,0,0), (0,0,1), 90)
) 

def Superellisse(raggio_y, raggio_z, potenza, num_punti):   
    # raggio_y = 100 significa che si estende da y=-100 a y=+100, stessa cosa per raggio_z, mentre n è la potenza: 2=cerchio, >2 = più squadrata
    
    # Generazione punti
    punti = []
    for i in range(num_punti):
        t = 2 * math.pi * i / num_punti
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        y = math.copysign(pow(abs(cos_t), 2/potenza), cos_t) * raggio_y
        z = math.copysign(pow(abs(sin_t), 2/potenza), sin_t) * raggio_z
        punti.append((y, z))

    # Crea lo spline periodico
    spline_obj = (
        cq.Workplane("YZ")
        .spline(punti, periodic=True, includeCurrent=False)
        .val()
    )

    # Converte in Wire (credo)
    if isinstance(spline_obj, Edge):
        anello = Wire.assembleEdges([spline_obj])
    else:
        anello = spline_obj

    return anello
    
def FacciaLoft(corpo_importato,x_taglio):
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
    return contorno_loft,faccia_loft

#assegno delle variabili ai risultati della funzione Faccia_loft per non eseguirla più volte nel codice
contorno_loft,faccia_loft=FacciaLoft(corpo_importato,x_taglio)
contorno_loft2=FacciaLoft(corpo_importato,x_taglio2)[0]


offset_z = -135       # Serve a centrare i cerchi per creare il loft

# Caratteristiche del cono di punta
raggio_base = 220.0
raggio_cima = 150.0
altezza_tot = 110.0
altezza_punta = 140.0
angolo_punta = 0 # Ancora da implementare
loft = (
    faccia_loft
    .workplane()                  # Creo un workplane sulla faccia troncata del solido
    .add(contorno_loft)           #aggiungo il perimetro della faccia al workplane
    .toPending()                  # Indico che questo perimetro è il primo da usare per il loft
    
    .workplane()                  # Creo il secondo piano parallelo derivato dalla sezione 
    .add(contorno_loft2) 
#maggiore è il numero delle sezioni maggiore è la precisione dell'attacco tra corpo e punta
#inoltre la precisione è anche variata dalla "variazione_sezioni" (riga 4)

    .workplane(offset=120)        # Creo il terzo piano parallelo
    .moveTo(0,offset_z)           # Serve a centrare il cerchio lungo z
     # Sarebbe bello trovare un modo per centrarlo indipendentemente dall'oggetto
    .circle(raggio_base)                  # Secondo profilo guida del loft

    .workplane(offset=altezza_punta)      # Creo il quarto piano parallelo per allineare la tangenza
    .moveTo(0,offset_z)                   # Serve a centrare il cerchio lungo z
    .circle(raggio_cima)

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
    .spline([(0, raggio_cima),
             (altezza_tot, 0)], 
            tangents=[(altezza_punta, raggio_cima-raggio_base),
                      (-1,0.6)])  # Da qui posso modificare la tangenza sulla punta
    .lineTo(0, 0)
    .close()
    .revolve(360.0, (0,0), (1, 0))    # Faccio ruotare intorno all'asse X
   )
   
result = loft.union(propeller_nose)
show_object(result)
