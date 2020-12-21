"""
Mediante este script se generan imagenes de ampollas a partir de un blister. Se tienen dos modos de recortar las ampollas.
    - Modo Recorte Bruto: Se debe de especificar el numero de ampollas por blister (imagen), y en caso de que existiese un offset inicial/final en la imagen del
      blister donde no existe ampolla,  se deberia de indicar este valor. Se divide la imagen en partes iguales, y se obtienen asi los contornos de las ampollas.
    - Modo Detectar Ampollas: Se detecta un determinado color en la imagen (el de la ampolla), y mediante una mascara, un filtro gaussiano,
      y un detector de bordes canny, se obtienen los contornos de las diferentes ampollas.
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
from dataset_config import TIPOS_AMPOLLAS


DETECTAR_AMPOLLAS = 0
RECORTE_BRUTO = 1
OFFSET_SIN_AMPOLLA = 80
N_AMPOLLAS = 5

PATH_DATASET_CLASIFICACION_TIPOS_AMPOLLAS = f'./dataset/dataset-clasificacion-tipos-ampollas'
PATH_IMGS = f'./dataset/dataset-original-blisters/Imagenes'
PATH_ANNS = f'./dataset/dataset-original-blisters/Anotaciones'
PATH_IMGS_CROP = f'./dataset/dataset-clasificacion-tipos-ampollas/Imagenes_aux'


def crear_carpetas_tipos_ampolla(diccionario_tipos_ampolla=TIPOS_AMPOLLAS, path_destino=PATH_DATASET_CLASIFICACION_TIPOS_AMPOLLAS):

    paths_nuevas_carpetas = []

    for keys, values in TIPOS_AMPOLLAS.items():
        path_nueva_carpeta = os.path.join(path_destino, values)
        paths_nuevas_carpetas.append(path_nueva_carpeta)
        try:
            os.mkdir(path_nueva_carpeta)
        except:
            print(f'La carpeta {values} ya existe')

    return paths_nuevas_carpetas


def crear_carpetas_auxiliares(PATH_IMGS_CROP=PATH_IMGS_CROP):
    try:
        os.mkdir(PATH_IMGS_CROP)

    except:
        print('Las carpetas auxiliares ya existen')


def elimina_carpetas_auxiliares(PATH_IMGS_CROP=PATH_IMGS_CROP):

    shutil.rmtree(PATH_IMGS)


def obtener_paths_imagenes(path=PATH_IMGS):
    paths_imagenes = glob.glob(f"{path}/*.png")

    return paths_imagenes


def obtener_paths_anotaciones(path=PATH_ANNS):
    paths_anotaciones = glob.glob(f"{path}/*.xml")

    return paths_anotaciones


def obtener_tamaño_imagen_total(path_imagen):
    img = cv2.imread(path_imagen)
    alto, ancho, profundidad = img.shape

    return alto, ancho


def obtener_tamaño_imagen_recortada(alto, ancho, path_imagen, cantidad_imagenes=N_AMPOLLAS):

    ancho_crop = int((ancho-OFFSET_SIN_AMPOLLA)/cantidad_imagenes)
    alto_crop = alto

    contornos = []
    for i in range(cantidad_imagenes):

        if 'I' == path_imagen[-5]:

            contornos.append([OFFSET_SIN_AMPOLLA + ancho_crop*i,
                              300, OFFSET_SIN_AMPOLLA + ancho_crop*(i + 1), 1700])

        if 'D' == path_imagen[-5]:
            contornos.append([ancho_crop*i,
                              300, ancho_crop*(i + 1), 1700])

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


def recorta_imagen_por_contornos(path_imagen, contorno, paths_nuevas_imagenes, indice):

    img = cv2.imread(path_imagen)

    xmin = contorno[0]
    ymin = contorno[1]
    xmax = contorno[2]
    ymax = contorno[3]

    img_crop = img[ymin:ymax, xmin:xmax]

    clasifica_imagen_en_carpeta(path_imagen, img_crop, indice)


def clasifica_imagen_en_carpeta(path_imagen, imagen_crop, indice):

    tipo_ampolla = (path_imagen.split('\\')[-1]).split("_")[-2]
    nombre_imagen = (path_imagen.split('\\')[-1])[:-4]+f'_{indice+1}'+'.png'

    nombre_tipo_ampolla = TIPOS_AMPOLLAS[tipo_ampolla]

    for i in paths_nuevas_carpetas:
        if nombre_tipo_ampolla in i:
            nuevo_path_parent = i
            break

    nuevo_path_imagen = os.path.join(nuevo_path_parent, nombre_imagen)

    cv2.imwrite(nuevo_path_imagen, imagen_crop)


def comprueba_todas_ampollas_iguales(path_anotacion):

    anotacion = ET.parse(path_anotacion)
    anotacion_aux = copy.deepcopy(anotacion)
    roots = anotacion_aux.getroot()

    for indice_root, root in enumerate(roots):
        if indice_root == 0:
            continue

        ampollas_distintas = 0

        for child in root:

            data_string = child.text

            if data_string != '-':
                ampollas_distintas += 1

    if ampollas_distintas > 1:
        return 1

    else:
        return 0


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

        elif ancho_defecto / ancho_contorno > 0.5:
            if producto:
                return 1

        if producto == 0:
            nuevas_coordenadas_defecto.append(
                [nueva_xmin, nueva_ymin, nueva_xmax, nueva_ymax])

    return nuevas_coordenadas_defecto


paths_nuevas_carpetas = crear_carpetas_tipos_ampolla()
# crear_carpetas_auxiliares()
paths_imagenes = obtener_paths_imagenes()
paths_anotaciones = obtener_paths_anotaciones()


for indice, path_imagen in enumerate(paths_imagenes):

    if RECORTE_BRUTO:
        alto, ancho = obtener_tamaño_imagen_total(path_imagen)
        contornos_ampollas = obtener_tamaño_imagen_recortada(
            alto, ancho, path_imagen)

        path_anotacion = paths_anotaciones[indice]

        for indice, contorno in enumerate(contornos_ampollas):

            existen_ampollas_distintas = comprueba_todas_ampollas_iguales(
                path_anotacion)

            if existen_ampollas_distintas:
                continue

            else:
                recorta_imagen_por_contornos(
                    path_imagen, contorno, paths_nuevas_carpetas, indice)

    if DETECTAR_AMPOLLAS:
        contornos_ampollas = obtener_contornos_ampollas(path_imagen)
        path_anotacion = paths_anotaciones[indice]

        for indice, contorno in enumerate(contornos_ampollas):
            nuevo_path_anotacion = genera_anotacion_en_contorno_ampolla(
                path_anotacion, contorno, indice)
            crop_imagen_por_contornos(
                path_imagen, contorno, nuevo_path_anotacion)

# elimina_carpetas_principales()
# cambia_nombre_carpetas_principales()
