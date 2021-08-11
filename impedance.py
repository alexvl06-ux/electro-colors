#--------------------------------------------------------------------------------------------------
#--------------------Extraccion de impedancias en escala de color----------------------------------
#--------------------------------------------------------------------------------------------------
#-------------Alexis Rafael del Carmen Ávila Ortiz--------CC 1083555169----------------------------
#-------------alexis.avila@udea.edu.co--------------------Wpp +57 305 2230574----------------------
#--------------------------------------------------------------------------------------------------
#-------------Yorguin José Mantilla Ramos-----------------CC 1127617499----------------------------
#-------------yorguinj.mantilla@udea.edu.co---------------Wpp +57 311 5154452----------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#----------------------Estudiantes Facultad de Ingenieria  ----------------------------------------
#--------Curso Básico de Procesamiento de Imágenes y Visión Artificial-----------------------------
#--------------------------Agosto de 2021----------------------------------------------------------
#--------------------------------------------------------------------------------------------------
import cv2                          # Para el procesamiento de Imagenes
import numpy as np                  # Para manejo de matricesS
import os                           # Para la manipulacion del sistema de archivos
import shutil                       # Para la manipulacion del sistema de archivos

#--------------------------------------------------------------------------------------------------
#-------------Variables de entrada-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

PLOT = False                        # Para controlar si queremos visualizar el procesamiento
                                    # durante el run-time

INPUT_DIR = 'images'                # Directorio donde se encuentran las imagenes originales
                                    # que se van a procesar.
OUTPUT_DIR = '.rois'                # Directorio donde se va a guardar el resultado de procesamiento
                                    # de cada una de las imagenes.

#--------------------------------------------------------------------------------------------------
#-------------Parametros constantes-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

# Definimos dos listas que siguen el mismo orden para representar el mapeo de un color a un valor
# de impendancia: COLOR[i] --> IMPEDANCIA[i].     

# En un futuro la idea es que estas dos listas se obtengan de forma automatica
# desde la imagen. Sin embargo ya que solo en raras ocasiones cambia, por ahora
# se mantiene como un parametro constante en la ejecucion.

Z_COLORS = [(255,0,255),            # Esta lista contiene n-tuplas de 3 posiciones.  
(128,0,128),                        # Cada una representando un color en formato RGB,
(0,0,255)  ,                        # es decir: (R,G,B)                              
(0,0,192)  ,                        
(0,0,128)  ,                        
(0,128,192),                        
(0,192,192),
(0,255,0)  ,
(0,192,0)  ,
(0,128,0)  ,
(192,192,0),
(255,0,0)  ,
(192,0,0)  ,
(128,0,0)  ,
(63,0,0)   ]

K = 1000                            # Sufijo K para abreviar kilo-ohms
Z_VALUES = [50*K  ,                 # Lista de impedancias, en el mismo orden que los colores
46.8*K,                             # De tal forma que al indexar ambas en un mismo sub-indice
43.6*K,                             # se obtienen el color y la impedancia correspondiente y 
40.4*K,                             # ligados entre si.
37.1*K,
33.9*K,
30.7*K,
27.5*K,
24.3*K,
21.1*K,
17.9*K,
14.6*K,
11.4*K,
8.2*K ,
5*K   ]


def plot_fun(x,title='untitled',func_sig='',plot=False,waitkey=False):
    """Procedimiento auxiliar para graficar y esperar
    la entrada del usuario si es requerido.
    x : np.ndarray
        La imagen a graficar
    title: str
        Titulo de la imagen
    func_sig: str
        Firma para proveer contexto
    plot: bool
        Indica si graficar o no la imagen.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.
    Returns
    -------
    None
    """
    name = func_sig+title
    if plot:                                                # Si modo de graficacion activo
        cv2.imshow(name, x)                                 # Graficamos la imagen
        if waitkey:                                         # Esperamos la entrada del usuario
            cv2.waitKey()                                   # de ser solicitado

def remover_exterior(img,plot=False,waitkey=False):
    """Elimina la ventana externa para quedar solo con 
    los electrodos,la escala y el fondo blanco.

    Parameters
    ----------
    img: arreglo de numpy de una imagen BGR
        La imagen a procesar. Dimensiones (altura,ancho,3 capas de colores)
    plot: bool
        Indica si graficar o no la imagen a medida que es procesada.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.
    Returns
    -------
    list:
        [imagen original
        imagen original con negro en lo removido,
        imagen recortada]
    """

    func_signature = 'RemoverExterior:'     # Firma de la funcion para identificar 
                                            # sus impresiones en consola y titulos

    all_images = []                                                 # Lista para ir guardando las imagenes a medida
                                                                    # de que avanzamos en el procesamiento (historial)
    all_titles = []                                                 # Lista para guardar metadatos del historial

    title = 'Imagen Entrante'                                       # Solo una variable para guardar metadatos del historial
    plot_fun(img,title,func_signature,plot,waitkey)                 # Graficacion si es solicitada
    all_images.append(np.copy(img))                                 # Añadir imagen al historial
    all_titles.append(title)                                        # Añadir metadatos

    # Objetivo: Extraer contornos de aquello que es blanco,
    # es decir, el fondo del interior de la imagen.

    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                             # Convertimos a escala de grises 
                                                                               # para facilitar la discriminacion del blanco entre lo demas
    title = 'Imagen Escala de Grises'
    plot_fun(imgray,title,func_signature,plot,waitkey)                         # Graficacion si es solicitada
    all_images.append(np.copy(imgray))                                         # Añadir imagen al historial
    all_titles.append(title)                                                   # Añadir metadatos

    # Binarizacion, permite identificar lo "muy blanco" en escala de grises.
    bin_low = 250                                                               # Seleccionamos umbrales muy selectivos
    bin_high = 255                                                              # Ya que el blanco que buscamos es practicamente puro
    ret, thresh = cv2.threshold(imgray, bin_low, bin_high, cv2.THRESH_BINARY)   # La binarizacion en si.

    title = 'Imagen Binarizada'
    plot_fun(thresh,title,func_signature,plot,waitkey)                          # Graficacion si es solicitada
    all_images.append(np.copy(thresh))                                          # Añadir imagen al historial
    all_titles.append(title)                                                    # Añadir metadatos

    # Extraccion de contornos
    # Esto se hara en el modo RETR_EXTERNAL, retornando asi solo los contornos exteriores (del cual el fondo blanco hace parte)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Busqueda de contornos

    # De los contornos extraidos, el fondo blanco sera el contorno mas grande
    # Usamos esta caracteristica para identificarlo

    assert len(contours) != 0,'No se pudieron encontrar contornos.'           # Aseguramos que se haya podido algun contorno
                                                                              # De lo contrario damos error
    # draw in blue the contours that were founded
    #cv2.drawContours(output, contours, -1, 255, 3)

    # find the biggest countour (c) by the area
    c = max(contours, key = cv2.contourArea)
    x,y,w,h = cv2.boundingRect(c)
    cropped_image = img[y:y+h, x:x+w]
    contour_sizes = [cv2.contourArea(contour) for contour in contours]
    biggest_contour = max(contour_sizes)
    # draw the biggest contour (c) in green
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

    # cv2.imshow("Result", np.hstack([img, output]))

    # cnt = contours[0]
    # cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
    idx = contour_sizes.index(biggest_contour)
    # The index of the contour that surrounds your object
    mask = np.zeros_like(imgray) # Create mask where white is what we want, black otherwise
    cv2.drawContours(mask, contours, idx, 255, -1) # Draw filled contour in mask

    
    #cv2.imshow("Input img", mask)
    out = np.zeros_like(img) # Extract out the object and place into output imgs
    out[mask == 255] = img[mask == 255]
    #cv2.imshow("Input img", out)
    #cv2.waitKey()
    return out,cropped_image

listOfFiles = [f for f in os.listdir(INPUT_DIR)]
if os.path.isdir(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

for image in listOfFiles:
    name,ext=os.path.splitext(image)
    folder = os.path.join('.rois',name+'_'+ext)
    img = cv2.imread(os.path.join(INPUT_DIR,image))
    # Nos quedamos con el contorno blanco y lo que este adentro
    _,img = remover_exterior(img) # keep the cropped
    
    original = img.copy()
    cv2.imshow('s',img)
    cv2.waitKey()
    # negro falta

    def get_dist(a,o):
        ds = []
        for i,_ in enumerate(a):
            ds.append( (a[i]-o[i])**2)
        
        return np.sqrt(np.sum(ds))

    def z_mapping(bgr,Z_COLORS,Z_VALUES,radii=0):
        dists = [get_dist(bgr,o) for o in Z_COLORS]
        idx = np.argmin(dists)
        return Z_VALUES[idx],np.min(dists)

    # Segmentacion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('s',gray)
    # cv2.waitKey()

    blurred = gray.copy()
    # blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # blurred = cv2.GaussianBlur(blurred, (3, 3), 0)
    # blurred = cv2.GaussianBlur(blurred, (3, 3), 0)

    # cv2.imshow('s',blurred)
    # cv2.waitKey()

    canny = cv2.Canny(blurred, 200, 255, 1)
    # cv2.imshow('s',canny)
    # cv2.waitKey()
    kernel = np.ones((5,5),np.uint8)
    # quitar letras internas
    dilate = canny.copy()#cv2.dilate(canny, kernel, iterations=2)
    #set(dilate.flatten().tolist())
    #dilate[np.where(dilate == 255)] = [0]
    #im[np.all(im == (0, 255, 0), axis=-1)] = (255,255,255)
    #cv2.imshow('s',dilate)
    #cv2.waitKey()

    # Find external contours (no importa el dilate??)
    #cnts = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    #cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    os.makedirs(folder,exist_ok=True)

    # Iterate thorugh contours and filter for ROI
    img_number = 0
    contour_sizes = [cv2.contourArea(contour) for contour in cnts]
    # calcular areas para identificar regiones outlier
    contour_areas =[]
    for c in cnts:
        _,_,w,h =cv2.boundingRect(c)
        contour_areas.append(w*h)

    #plt.boxplot(contour_sizes)
    # show plot
    #plt.show()
    # Discriminar solo electrodos
    def foo(area,low=700,high=3000):
        if area > low and area < high:
            return True
        else:
            return False

    cnts = [c  for i,c in enumerate(cnts) if foo(contour_areas[i]) ]

    contour_sizes = [cv2.contourArea(contour) for contour in cnts]
    contour_areas =[]
    for c in cnts:
        _,_,w,h =cv2.boundingRect(c)
        contour_areas.append(w*h)


    insides =[]
    radii = 10
    for i,c in enumerate(cnts):
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (36,255,12), 1)
        ROI = dilate[y:y+h, x:x+w]
        # para quedarnos con el color y no con la letra
        dilate2 = cv2.dilate(ROI, kernel, iterations=2)
        cv2.imshow('s',dilate2)
        # cnts2,_ = cv2.findContours(ROI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # # maybe i cant discriminate by color/contour because they may have the same color
        # if len(cnts2):
        #     cnts3 = cv2.findContours(ROI, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # Mascara del contorno a la imagen con colores
        ROI = original[y:y+h, x:x+w]

        # discrimination by color does not work, they may have the same color
        #colors = np.unique(ROI.copy().reshape(-1, ROI.shape[-1]), axis=0, return_counts=False).shape[0]
        #insides.append((len(cnts2),colors))
        

        #discriminate by size and split in the y middle
        if contour_areas[i] > 1500:
            ROI1 = original[y:y+h//2, x+int(np.floor(w*0.25)):x+w]
            ROI2 = original[y+h//2:y+h, x:x+int(np.floor(w*0.75))]
            ROIS = [ROI1,ROI2]
            #insides.append((len(cnts2),colors))
        else:
            ROIS = [ROI]
        chars =[]
        for j,r in enumerate(ROIS):
            colors,counts = np.unique(r.copy().reshape(-1, r.shape[-1]), axis=0, return_counts=True)
            index=np.argmax(counts)
            color = colors[index]
            z,mindist = z_mapping(color,Z_COLORS,Z_VALUES)
            insides.append((i,j,z,mindist))
            cv2.imwrite(os.path.join(folder,"ROI_{}_{}__{}_{}.png".format(i,j,z,mindist)), r)

    #cv2.imshow('canny', canny)
    #cv2.imshow('img', img)
    #cv2.waitKey(0)