"""
Mediante este script se generan imagenes y anotaciones de ampollas a partir de un blister. Se tienen dos modos de recortar las ampollas.
    - Modo Recorte Bruto: Se debe de especificar el numero de ampollas por blister (imagen), y en caso de que existiese un offset inicial/final en la imagen del
      blister donde no existe ampolla,  se deberia de indicar este valor. Se divide la imagen en partes iguales, y se obtienen asi los contornos de las ampollas.
    - Modo Detectar Ampollas: Se detecta un determinado color en la imagen (el de la ampolla), y mediante una mascara, un filtro gaussiano,
      y un detector de bordes canny, se obtienen los contornos de las diferentes ampollas.

A tavés de los contornos obtenidos, se analizan las coordenadas de las anotaciones. De manera que si una anotacion intersecta o esta dentro del contorno,
esta anotacion se dibujara dentro de sus limites, manteniendo en el diccionario el tipo de defecto que existe. Se puede configurar el valor a partir del cual,
un defecto es demasiado pequeño como para aparecer en la imagen (puede ser que en la imagen contigua este el defecto, y en la presente unicamente estamos
viendo la extension de los limites contorno del defecto)

Se ha de definir la ruta original de las Imagenes y las Anotaciones, y la ruta final donde se guardaran los recortes.
"""
import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt
from operator import itemgetter
from heapq import nlargest
import xml.etree.cElementTree as ET
import copy
import pandas as pd
import io
import os
import sys
import shutil


DETECTAR_AMPOLLAS = 0
RECORTE_BRUTO = 1
OFFSET_SIN_AMPOLLA = 80
N_AMPOLLAS = 5

folder = 'train'

PATH_IMGS = f'./dataset/dataset-deteccion-defectos-ampollas/ToDrive/{folder}/Imagenes'
PATH_ANNS = f'./dataset/dataset-deteccion-defectos-ampollas/ToDrive/{folder}//Anotaciones'
PATH_IMGS_CROP = f'./dataset/dataset-deteccion-defectos-ampollas/ToDrive/{folder}//Imagenes_aux'
PATH_ANNS_CROP = f'./dataset/dataset-deteccion-defectos-ampollas/ToDrive/{folder}//Anotaciones_aux'

{"SIN DEFECTO": ["sin_defecto", '-', '0'],
 'MORF. CABEZA AMPOLLA': ['amp_morf_cabeza', '-', '1'],
 "MORF. CUELLO AMPOLLA": ["amp_morf_cuello", '-', '2'],
 "IMP. AMPOLLA": ["amp_imp", '-', '3'],
 "IMP. BLISTER": ["blis_imp", '-', '4']}

DICCIONARIO_COORDENADAS_DEFECTOS = {"amp_imp": 0,
                                    "amp_morf_cabeza": 1,
                                    "amp_morf_cuello": 2,
                                    "blis_imp": 3,
                                    "sin_defecto": 4,
                                    "babe_vitaminC": 11,
                                    "babe_bicalm": 12,
                                    "babe_proteos2f": 13}


def crear_carpetas_auxiliares(PATH_IMGS_CROP=PATH_IMGS_CROP, PATH_ANNS_CROP=PATH_ANNS_CROP):
    try:
        os.mkdir(PATH_IMGS_CROP)
        os.mkdir(PATH_ANNS_CROP)
    except:
        print('Las carpetas auxiliares ya existen')


def elimina_carpetas_principales(PATH_IMGS=PATH_IMGS, PATH_ANNS=PATH_ANNS):

    shutil.rmtree(PATH_IMGS)
    shutil.rmtree(PATH_ANNS)


def cambia_nombre_carpetas_principales(PATH_IMGS=PATH_IMGS, PATH_ANNS=PATH_ANNS, PATH_IMGS_CROP=PATH_IMGS_CROP, PATH_ANNS_CROP=PATH_ANNS_CROP):
    os.rename(PATH_IMGS_CROP, PATH_IMGS)
    os.rename(PATH_ANNS_CROP, PATH_ANNS)


def obtener_paths_imagenes(path=PATH_IMGS):
    paths_imagenes = glob.glob(f"{path}/*.png")

    return paths_imagenes


def obtener_paths_anotaciones(path=PATH_ANNS):
    paths_anotaciones = glob.glob(f"{path}/*.xml")

    return paths_anotaciones


def obtener_tamaño_imagen(path_imagen):
    img = cv2.imread(path_imagen)
    alto, ancho, profundidad = img.shape

    return alto, ancho


def obtener_tamaño_imagen_crop(alto, ancho, path_imagen, cantidad_imagenes=N_AMPOLLAS):

    ancho_crop = int((ancho-OFFSET_SIN_AMPOLLA)/cantidad_imagenes)
    alto_crop = alto

    contornos = []
    for i in range(cantidad_imagenes):

        if 'I' == path_imagen[-5]:

            contornos.append([OFFSET_SIN_AMPOLLA + ancho_crop*i,
                              0, OFFSET_SIN_AMPOLLA + ancho_crop*(i + 1), alto])

        if 'D' == path_imagen[-5]:
            contornos.append([ancho_crop*i,
                              0, ancho_crop*(i + 1), alto])

    return contornos


def crop_imagen(path_imagen, alto_crop, ancho_crop, alto, ancho):

    ancho_ini = 0
    alto_ini = 0
    indice = 1
    img = cv2.imread(path_imagen)

    while ancho_ini < ancho:
        img_crop = img[alto_ini: alto, ancho_ini: ancho_crop*indice]
        ancho_ini += ancho_crop
        guarda_imagen_crop(path_imagen, indice, img_crop)
        indice += 1


def crop_imagen_por_contornos(path_imagen, contorno, path_anotacion, PATH_NUEVAS_IMGS=PATH_IMGS_CROP):

    path_anotacion_aux = copy.deepcopy(path_anotacion)

    img = cv2.imread(path_imagen)

    xmin = contorno[0]
    ymin = contorno[1]
    xmax = contorno[2]
    ymax = contorno[3]

    img_crop = img[ymin: ymax, xmin: xmax]

    nuevo_nombre_imagen = path_anotacion_aux.split("\\")[-1][: -3]+'png'
    nuevo_path_imagen = os.path.join(PATH_NUEVAS_IMGS, nuevo_nombre_imagen)

    cv2.imwrite(nuevo_path_imagen, img_crop)


def guarda_imagen_crop(path_imagen, indice, img_crop, path_imagenes_crop=PATH_IMGS_CROP):
    nombre_imagen = path_imagen.split("\\")[-1]
    tipo_defecto = nombre_imagen.split("_")[-3]
    nombre_imagen = f"{nombre_imagen[:-4]}_{indice}.png"
    cv2.imwrite(f'{path_imagenes_crop}/{nombre_imagen}', img_crop)


def forma_nombre_anotacion(path_anotacion, labels_defectos, numero_producto, indice_ampolla, PATH_NUEVAS_ANNS=PATH_ANNS_CROP):

    path_anotacion_aux = copy.deepcopy(path_anotacion)
    nombre_anotacion = path_anotacion_aux.split("\\")[-1]
    componentes_nombre = nombre_anotacion.split("_")

    componentes_nombre[2] = 'C'+labels_defectos
    componentes_nombre[3] = numero_producto

    nuevo_nombre_anotacion = ""

    for indice, componente in enumerate(componentes_nombre):
        if indice == 0:
            nuevo_nombre_anotacion = nuevo_nombre_anotacion + componente
            continue
        nuevo_nombre_anotacion = nuevo_nombre_anotacion+'_'+str(componente)

    nuevo_nombre_anotacion = nuevo_nombre_anotacion[: -4] + \
        f'_{indice_ampolla}'+'.xml'

    nuevo_path_anotacion = os.path.join(
        PATH_NUEVAS_ANNS, nuevo_nombre_anotacion)

    return nuevo_path_anotacion


def obtener_contornos_ampollas(path_imagen):

    off_X = 50
    off_Y = 150

    # Cargamos la imagen
    image = cv2.imread(path_imagen)
    alto, ancho, _ = image.shape

    original = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image = cv2.GaussianBlur(image, (133, 133), 0)

    # original = cv2.resize(original, (700, 700))
    # image = cv2.resize(image, (700, 700))
    # alto, ancho, _ = image.shape

    lower = np.array([25, 127, 90], dtype="uint8")
    upper = np.array([35, 255, 255], dtype="uint8")
    mask = cv2.inRange(image, lower, upper)
    canny = cv2.Canny(mask, 50, 250)

    # cv2.imshow('mask', mask)
    # cv2.imshow("canny", canny)

    cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    areas_contornos = []

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        areas_contornos.append(w * h)

    areas_indices_altos = nlargest(
        5, enumerate(areas_contornos), itemgetter(1))

    indices_altos = [index for index, value in nlargest(
        5, enumerate(areas_contornos), itemgetter(1))]

    contornos_ampollas = []

    ymin = 100000000
    ymax = 0

    for indice, c in enumerate(cnts):
        if indice in indices_altos:
            x, y, w, h = cv2.boundingRect(c)

            if y < ymin:
                ymin = y
            if (y + h) > ymax:
                ymax = y + h

    for indice, c in enumerate(cnts):
        if indice in indices_altos:
            x, y, w, h = cv2.boundingRect(c)

            if x + w + off_X > ancho:
                cv2.rectangle(original, (x-off_X, ymin-off_Y),
                              (x + w, ymax + off_Y), (0, 255, 0), 2)

                contornos_ampollas.append(
                    [x-off_X, ymin-off_Y, x + w, ymax + off_Y])

            elif x - off_X < 0:
                cv2.rectangle(original, (x, ymin-off_Y),
                              (x + w + off_X, ymax + off_Y), (0, 255, 0), 2)

                contornos_ampollas.append(
                    [x, ymin-off_Y, x + w + off_X, ymax + off_Y])
            else:
                cv2.rectangle(original, (x-off_X, ymin-off_Y),
                              (x + w + off_X, ymax + off_Y), (0, 255, 0), 2)

                contornos_ampollas.append(
                    [x-off_X, ymin-off_Y, x + w + off_X, ymax + off_Y])

    # cv2.imshow('mask', mask)
    # cv2.imshow('original', original)
    plt.figure()
    plt.imshow(original)
    plt.show()

    plt.figure()
    plt.imshow(mask)
    plt.show()

    plt.figure()
    plt.imshow(canny)
    plt.show()
    cv2.waitKey()

    return contornos_ampollas


def genera_anotacion_en_contorno_ampolla(path_anotacion, coordenadas_contorno, indice):
    producto_detectado = 0
    anotacion = ET.parse(path_anotacion)
    anotacion_aux = copy.deepcopy(anotacion)
    roots = anotacion_aux.getroot()
    label_defectos = ""

    for indice_root, root in enumerate(roots):
        if indice_root == 0:
            for child in root:

                data_string_old = child.text

                if data_string_old == '-':
                    data_string_new = data_string_old

                if data_string_old != '-':
                    boxes = []
                    data = io.StringIO(data_string_old.strip())
                    header = ["xmin", "ymin", "xmax", "ymax"]
                    df = pd.read_csv(data, sep=",", header=None,
                                     names=header, lineterminator=";")

                    for index, row in df.iterrows():
                        xmin = int((row['xmin']))
                        ymin = int((row['ymin']))
                        xmax = int((row['xmax']))
                        ymax = int((row['ymax']))
                        boxes.append([xmin, ymin, xmax, ymax])

                    # Comprobamos si el defecto se encuentra dentro o intersecta con el contorno de la ampolla:
                    nuevas_coordenadas_defecto = comprobar_interseccion_defecto_y_contorno_ampolla(
                        coordenadas_contorno, boxes, 0)

                    if nuevas_coordenadas_defecto != []:

                        # Obtenemos el nombre del tipo de defecto:
                        numero_defecto = DICCIONARIO_COORDENADAS_DEFECTOS[child.tag]
                        label_defectos = label_defectos+f"{numero_defecto}"

                        # Rescribimos la anotacion
                        data_string_new = ""

                        for i in nuevas_coordenadas_defecto:
                            c = 0
                            for j in i:
                                if c == 0:
                                    data_string_new += f"{j},"
                                elif c == 1:
                                    data_string_new += f"{j},"
                                elif c == 2:
                                    data_string_new += f"{j},"
                                elif c == 3:
                                    data_string_new += f"{j}; "
                                c += 1

                    else:
                        data_string_new = "-"

                child.text = child.text.replace(
                    data_string_old, data_string_new)

        if indice_root == 1:

            for child in root:

                data_string_old = child.text

                if data_string_old == '-':
                    data_string_new = data_string_old

                if data_string_old != '-':
                    boxes = []
                    data = io.StringIO(data_string_old.strip())
                    header = ["xmin", "ymin", "xmax", "ymax"]
                    df = pd.read_csv(data, sep=",", header=None,
                                     names=header, lineterminator=";")

                    for index, row in df.iterrows():
                        xmin = int((row['xmin']))
                        ymin = int((row['ymin']))
                        xmax = int((row['xmax']))
                        ymax = int((row['ymax']))
                        boxes.append([xmin, ymin, xmax, ymax])

                    area_coordenadas_contorno = (coordenadas_contorno[2]-coordenadas_contorno[0])*(
                        coordenadas_contorno[3] - coordenadas_contorno[1])

                    area_boxes_ppal = (xmax - xmin) * (ymax - ymin)

                    ampolla_error = comprobar_interseccion_defecto_y_contorno_ampolla(
                        coordenadas_contorno, boxes, 1)

                    if producto_detectado == 0:
                        producto = child.tag
                        numero_producto = DICCIONARIO_COORDENADAS_DEFECTOS[producto]
                        producto_detectado = 1

                    if area_boxes_ppal / area_coordenadas_contorno < 2 and ampolla_error:
                        producto = child.tag
                        numero_producto = DICCIONARIO_COORDENADAS_DEFECTOS[producto]
                        producto_detectado = 1

                    coordenadas_producto = [
                        0, 0, coordenadas_contorno[2]-coordenadas_contorno[0], coordenadas_contorno[3]]

            for child in root:

                data_string_old = child.text

                if producto == child.tag:

                    # Rescribimos la anotacion
                    data_string_new = ""

                    c = 0
                    for j in coordenadas_producto:
                        if c == 0:
                            data_string_new += f"{j},"
                        elif c == 1:
                            data_string_new += f"{j},"
                        elif c == 2:
                            data_string_new += f"{j},"
                        elif c == 3:
                            data_string_new += f"{j}; "
                        c += 1

                    child.text = child.text.replace(
                        data_string_old, data_string_new)

                else:
                    data_string_new = '-'
                    child.text = child.text.replace(
                        data_string_old, data_string_new)

        if label_defectos == "":
            label_defectos = '4'

    nuevo_path_anotacion = forma_nombre_anotacion(
        path_anotacion, label_defectos, numero_producto, indice)

    anotacion_aux.write(nuevo_path_anotacion)

    return nuevo_path_anotacion


def comprobar_interseccion_defecto_y_contorno_ampolla(coordendas_contorno, coordenadas_defectos, producto):

    xmin_contorno = coordendas_contorno[0]
    ymin_contorno = coordendas_contorno[1]
    xmax_contorno = coordendas_contorno[2]
    ymax_contorno = coordendas_contorno[3]

    ancho_contorno = xmax_contorno - xmin_contorno
    alto_contorno = ymax_contorno - ymin_contorno

    nuevas_coordenadas_defecto = []

    for box in coordenadas_defectos:
        xmin = box[0]
        ymin = box[1]
        xmax = box[2]
        ymax = box[3]

        # Arriba izquierda - Abajo derecha
        if ((xmin_contorno < xmin) and (ymin_contorno < ymin) and (xmax_contorno < xmax) and (ymax_contorno < ymax) and (xmin < xmax_contorno) and (ymin < ymax_contorno)) or ((xmin_contorno > xmin) and (ymin_contorno > ymin) and (xmax_contorno > xmax) and (ymax_contorno > ymax) and (xmin_contorno < xmax) and (ymin_contorno < ymax)):
            x_left = max(xmin_contorno, xmin)
            y_top = max(ymin_contorno, ymin)
            x_right = min(xmax_contorno, xmax)
            y_bottom = min(ymax_contorno, ymax)

        # Arriba derecha
        elif ((xmin_contorno < xmin) and (ymin_contorno > ymin) and (xmax_contorno < xmax) and (ymax_contorno > ymax) and (xmin < xmax_contorno) and (ymin_contorno < ymax)):
            x_left = xmin
            y_top = ymin_contorno
            x_right = xmax_contorno
            y_bottom = ymax

        # Abajo izquierda
        elif ((xmin_contorno > xmin) and (ymin_contorno < ymin) and (xmax_contorno > xmax) and (ymax_contorno < ymax) and (xmin_contorno < xmax) and (ymin < ymax_contorno)):
            x_left = xmin_contorno
            y_top = ymin
            x_right = xmax
            y_bottom = ymax_contorno

        # Arriba
        elif ((xmin_contorno < xmin) and (ymin_contorno > ymin) and (xmax_contorno > xmax) and (ymax_contorno > ymax) and (ymin_contorno < ymax) and (xmin < xmax_contorno)):
            x_left = xmin
            y_top = ymin_contorno
            x_right = xmax
            y_bottom = ymax

        # Derecha
        elif ((xmin_contorno < xmin) and (ymin_contorno < ymin) and (xmax_contorno < xmax) and (ymax_contorno > ymax) and (ymin_contorno < ymax) and (xmin < xmax_contorno)):
            x_left = xmin
            y_top = ymin
            x_right = xmax_contorno
            y_bottom = ymax

        # Abajo
        elif ((xmin_contorno < xmin) and (ymin_contorno < ymin) and (xmax_contorno > xmax) and (ymax_contorno < ymax) and (ymin_contorno < ymax) and (xmin < xmax_contorno)):
            x_left = xmin
            y_top = ymin
            x_right = xmax
            y_bottom = ymax_contorno

        # Izquierda
        elif ((xmin_contorno > xmin) and (ymin_contorno < ymin) and (xmax_contorno > xmax) and (ymax_contorno > ymax) and (ymin_contorno < ymax) and (xmax > xmin_contorno)):
            x_left = xmin_contorno
            y_top = ymin
            x_right = xmax
            y_bottom = ymax

        # Arriba ancho
        elif ((xmin_contorno > xmin) and (ymin_contorno > ymin) and (xmax_contorno < xmax) and (ymax_contorno > ymax) and (ymin_contorno > ymax) and (xmin_contorno < xmax)):
            x_left = xmin_contorno
            y_top = ymin_contorno
            x_right = xmax_contorno
            y_bottom = ymax

        # Bajo ancho
        elif ((xmin_contorno > xmin) and (ymin_contorno < ymin) and (xmax_contorno < xmax) and (ymax_contorno < ymax) and (ymax_contorno > ymin) and (xmin_contorno < xmax)):
            x_left = xmin_contorno
            y_top = ymin
            x_right = xmax_contorno
            y_bottom = ymax_contorno

        # Izquierda ancho
        elif ((xmin_contorno > xmin) and (ymin_contorno > ymin) and (xmax_contorno > xmax) and (ymax_contorno < ymax) and (ymin_contorno < ymax) and (xmin_contorno < xmax)):
            x_left = xmin_contorno
            y_top = ymin_contorno
            x_right = xmax
            y_bottom = ymax_contorno

        # Derecha ancho
        elif ((xmin_contorno < xmin) and (ymin_contorno > ymin) and (xmax_contorno < xmax) and (ymax_contorno < ymax) and (ymin_contorno < ymax) and (xmin_contorno < xmax)):
            x_left = xmin
            y_top = ymin_contorno
            x_right = xmax_contorno
            y_bottom = ymax_contorno

        # Horizontal
        elif ((xmin_contorno > xmin) and (ymin_contorno < ymin) and (xmax_contorno < xmax) and (ymax_contorno > ymax) and (ymin_contorno < ymax) and (xmin_contorno < xmax)):
            x_left = xmin_contorno
            y_top = ymin
            x_right = xmax_contorno
            y_bottom = ymax

        # Vertical
        elif ((xmin_contorno < xmin) and (ymin_contorno > ymin) and (xmax_contorno > xmax) and (ymax_contorno < ymax) and (ymin_contorno < ymax) and (xmin_contorno < xmax)):
            x_left = xmin
            y_top = ymin_contorno
            x_right = xmax
            y_bottom = ymax_contorno

        # Dentro
        elif (xmin_contorno <= xmin and ymin_contorno <= ymin and xmax_contorno >= xmax and ymax_contorno > ymax) or ((xmin_contorno >= xmin and ymin_contorno >= ymin and xmax_contorno <= xmax and ymax_contorno <= ymax)):
            x_left = xmin
            y_top = ymin
            x_right = xmax
            y_bottom = ymax

        else:
            continue

        nueva_xmin = x_left-xmin_contorno
        nueva_ymin = y_top - ymin_contorno
        nueva_xmax = x_right - xmin_contorno
        nueva_ymax = y_bottom - ymin_contorno

        ancho_defecto = nueva_xmax - nueva_xmin

        if ancho_defecto > ancho_contorno * 3:
            if producto:
                nuevas_coordenadas_defecto = 0
            continue

        elif ancho_defecto / ancho_contorno > 0.1:
            if producto:
                return 1

        if producto == 0:
            nuevas_coordenadas_defecto.append(
                [nueva_xmin, nueva_ymin, nueva_xmax, nueva_ymax])

    return nuevas_coordenadas_defecto


paths_imagenes = obtener_paths_imagenes()
paths_anotaciones = obtener_paths_anotaciones()
crear_carpetas_auxiliares()


for indice, path_imagen in enumerate(paths_imagenes):

    if RECORTE_BRUTO:
        alto, ancho = obtener_tamaño_imagen(path_imagen)
        contornos_ampollas = obtener_tamaño_imagen_crop(
            alto, ancho, path_imagen)

        path_anotacion = paths_anotaciones[indice]

        for indice, contorno in enumerate(contornos_ampollas):
            nuevo_path_anotacion = genera_anotacion_en_contorno_ampolla(
                path_anotacion, contorno, indice)
            crop_imagen_por_contornos(
                path_imagen, contorno, nuevo_path_anotacion)

    if DETECTAR_AMPOLLAS:
        contornos_ampollas = obtener_contornos_ampollas(path_imagen)
        path_anotacion = paths_anotaciones[indice]

        for indice, contorno in enumerate(contornos_ampollas):
            nuevo_path_anotacion = genera_anotacion_en_contorno_ampolla(
                path_anotacion, contorno, indice)
            crop_imagen_por_contornos(
                path_imagen, contorno, nuevo_path_anotacion)

elimina_carpetas_principales()
cambia_nombre_carpetas_principales()
