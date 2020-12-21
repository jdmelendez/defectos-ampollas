import PIL
from PIL import Image
import cv2
import os
import glob
import io
import numpy as np
import pandas as pd
import xml.etree.cElementTree as ET
import shutil
import imutils
import copy


# Obtenemos la ruta desde donde se ejecuta nuestro script
# dir_train = './dataset/dataset-deteccion-blisters/ToDrive/train'
# dir_test = './dataset/dataset-deteccion-blisters/ToDrive/test'
# dir_test = './dataset/dataset-deteccion-ampollas/ToDrive/test'
dir_train = './dataset/dataset-deteccion-defectos-ampollas/ToDrive/train'
dir_val = './dataset/dataset-deteccion-defectos-ampollas/ToDrive/val'

# ______________________________________________________________________________________________________________________
# FUNCION ROTACIÓN:


def rotacion_imagen(img_path, rt_degr):
    img = Image.open(img_path)

    return img.rotate(rt_degr, expand=1)

# img_rt_90 = rotate_img('Images/Screenshot.png', 90)
# img_rt_90.save('img_rt_90.png')

# def rotacion_imagen(imagen, angulo, centro=None, escala=1.0):
#     # Obtenemos ancho y alto
#     ancho = imagen.shape[1]
#     alto = imagen.shape[0]

#     if centro is None:
#         centro = (ancho // 2, alto // 2)

#     # Matriz de transformación, rotación
#     # M = cv2.getRotationMatrix2D(centro, angulo, escala)

#     # Aplicamos rotación a la imagen
#     # ImagenRotada = cv2.warpAffine(imagen, M, (ancho, alto))

#     ImagenRotada = imutils.rotate_bound(imagen, -angulo)

#     # Devolvemos la imagen rotada
#     return ImagenRotada


def rotacion_anotacion(boxes, imagen, angulo, centro=None):

    new_boxes = []
    # if angulo == 90 or angulo == 270:
    ancho = imagen.shape[1]
    alto = imagen.shape[0]

    h = imagen.shape[0]
    w = imagen.shape[1]

    centro_nuevo = (ancho // 2, alto // 2)
    centro = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(centro, angulo, 1)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - centro[0]
    M[1, 2] += (nH / 2) - centro[1]

    # else:
    ancho = imagen.shape[1]
    alto = imagen.shape[0]

    # c, s = np.cos(np.deg2rad(-angulo)), np.sin(np.deg2rad(-angulo))
    # R = np.array(((c, -s), (s, c)))

    # if centro is None:
    #     rc = np.array(((ancho // 2, alto // 2),)).T

    for j in boxes:
        xmin = int(j[0])
        ymin = int(j[1])
        xmax = int(j[2])
        ymax = int(j[3])

        width = xmax - xmin
        heigth = ymax - ymin

        coordenadas_min = [xmin, ymin, 1]
        coordenadas_max = [xmax, ymax, 1]

        calculadas_1 = np.dot(M, coordenadas_min)
        calculadas_2 = np.dot(M, coordenadas_max)

        # xmin_new = min(calculadas_1[0], calculadas_2[0])
        # xmax_new = max(calculadas_1[0], calculadas_2[0])
        # ymin_new = min(calculadas_1[1], calculadas_2[1])
        # ymax_new = max(calculadas_1[1], calculadas_2[1])

        xmin_new = int(calculadas_1[0])
        xmax_new = int(calculadas_2[0])
        ymin_new = int(calculadas_2[1])
        ymax_new = int(calculadas_1[1])

        # xmin = cx - 2*(xmin-cx)

        # x1 = xmin
        # y1 = ymin
        # x2 = xmin
        # y2 = ymax
        # x3 = xmax
        # y3 = ymax
        # x4 = xmax
        # y4 = ymin

        # pts = np.array(((x1, y1), (x2, y2), (x3, y3), (x4, y4))).T
        # pts_new = rc + (R @ (pts - rc))

        # xmin_new = int(min(pts_new[0]))
        # ymin_new = int(min(pts_new[1]))
        # xmax_new = int(max(pts_new[0]))
        # ymax_new = int(max(pts_new[1]))

        # heigth_new = width
        # width_new = heigth
        # xmax_new = xmin_new + heigth_new
        # ymax_new = ymin_new + width_new

        # if angulo == 180:
        #     heigth_new = heigth
        #     width_new = width
        #     xmax_new = xmin_new + width_new
        #     ymax_new = ymin_new +
        # nuevas_coordenadas = np.dot(M, j)

        # if angulo == 90:
        xmin_new_ok = min(xmin_new, xmax_new)
        xmax_new_ok = max(xmin_new, xmax_new)
        ymin_new_ok = min(ymin_new, ymax_new)
        ymax_new_ok = max(ymin_new, ymax_new)

        new_boxes.append([xmin_new_ok, ymin_new_ok, xmax_new_ok, ymax_new_ok])
    return new_boxes
# ______________________________________________________________________________________________________________________
# FUNCION INVERTIR


def invertir_imagen(imagen):
    ImagenInvertida = cv2.flip(imagen, 1)

    return ImagenInvertida


def invertir_anotacion(boxes, imagen, angulo, doble_operacion=0, centro=None):
    new_boxes = []
    ancho = imagen.shape[1]
    alto = imagen.shape[0]

    c, s = np.cos(np.deg2rad(-angulo)), np.sin(np.deg2rad(-angulo))
    R = np.array(((c, -s), (s, c)))

    if centro is None:
        rc = np.array(((ancho // 2, alto // 2),)).T

    for j in boxes:
        xmin = int(j[0])
        ymin = int(j[1])
        xmax = int(j[2])
        ymax = int(j[3])
        width = xmax - xmin
        heigth = ymax-ymin

        # x1 = xmin
        # y1 = ymin
        # x2 = xmin
        # y2 = ymax
        # x3 = xmax
        # y3 = ymax
        # x4 = xmax
        # y4 = ymin

        # pts = np.array(((x1, y1), (x2, y2), (x3, y3), (x4, y4))).T
        # pts_new = rc + R @ (pts - rc)

        # xmin_new = -xmin + ancho - width
        # ymin_new = ymin
        # heigth_new = heigth
        # width_new = width
        # xmax_new = xmin_new + width_new
        # ymax_new = ymin_new + heigth_new

        # if angulo == 90:
        # xmin_new_ok = min(xmin_new, xmax_new)
        # xmax_new_ok = max(xmin_new, xmax_new)
        # ymin_new_ok = min(ymin_new, ymax_new)
        # ymax_new_ok = max(ymin_new, ymax_new)
        xmin_new_ok = ancho-xmax
        xmax_new_ok = ancho-xmin
        ymin_new_ok = ymin
        ymax_new_ok = ymax

        # xmin_new_ok = min(xmin_new, xmax_new)
        # xmax_new_ok = max(xmin_new, xmax_new)

        new_boxes.append([xmin_new_ok, ymin_new_ok, xmax_new_ok, ymax_new_ok])

    return new_boxes
# ______________________________________________________________________________________________________________________
# FUNCION NUEVAS ANOTACIONES EN XML:


def new_anottation(anotacion_aux, imagen, angulo, transformacion, Nombre_Anotacion):

    anotacion = copy.deepcopy(anotacion_aux)
    roots = anotacion.getroot()

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

                    if transformacion == 'INV':
                        boxes_new = invertir_anotacion(boxes, imagen, angulo)
                    elif transformacion == 'ROT':
                        boxes_new = rotacion_anotacion(boxes, imagen, angulo)
                    elif transformacion == 'INV_ROT':
                        boxes_new_inv = invertir_anotacion(
                            boxes, imagen, 270, 1)
                        boxes_new = rotacion_anotacion(
                            boxes_new_inv, imagen, angulo)

                    data_string_new = ""
                    for i in boxes_new:
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

                child.text = child.text.replace(
                    data_string_old, data_string_new)

    anotacion.write(Nombre_Anotacion)

# _____________________________________________________________________________________________________________________
# FUNCION DE IMÁGENES Y ANOTACIONES


def lectura_imagenes_anotaciones(dir):
    # Buscamos las carpetas de imagenes y anotaciones
    carpetas = os.listdir(dir)

    # El archivo de la lista de carpetas ".py", lo quitamos de la lista
    carpetas = [x for x in carpetas if "." not in x]
    print("\n\nCARPETAS EXISTENTES:")
    print(carpetas)

    # Obtenemos las rutas de las distintas carpetas
    paths = []
    for i in range(len(carpetas)):
        paths.append(os.path.join(dir, carpetas[i]))

    # Vemos la cantidad de archivos de cada clase
    print("\nCANTIDAD DE ARCHIVOS EN CADA CARPETA:")

    cantidad_archivos = []
    for x in range(len(carpetas)):
        cantidad_archivos.append(os.listdir(paths[x]))
        print(
            f"\tCarpeta '{carpetas[x]}': {len(cantidad_archivos[x])} archivos")

    # if len(cantidad_archivos[0]) == len(cantidad_archivos[1]):
    #     print("Misma cantidad de archivos en cada carpeta --> CONTINUE !")
    # else:
    #     print("Distinta cantidad de archivos en cada carpeta --> STOP !")
    #     quit()

    # ______________________________________________________________________________________________________________________
    # LECTURA DE FICHEROS EN CARPETA

    # Imagenes:
    imagenes = [cv2.imread(file) for file in glob.glob(f"{paths[1]}/*.png")]
    nombres_imagenes = os.listdir(paths[1])
    paths_imagenes = glob.glob(f"{paths[1]}/*.png")

    # Anotaciones:
    anotaciones = [ET.parse(file)for file in glob.glob(f"{paths[0]}/*.xml")]
    nombres_anotaciones = os.listdir(paths[0])

    return imagenes, nombres_imagenes, anotaciones, nombres_anotaciones, paths_imagenes

# ______________________________________________________________________________________________________________________
# APLICAMOS LAS TRANSFORMACIONES:


def realiza_aumento_dataset(imagenes, nombres_imagenes, anotaciones, nombres_anotaciones, path, paths_imagenes):
    print(f"\n\nTransformando anotaciones...")

    for indice, nombre_anotacion in enumerate(nombres_anotaciones):

        print(f"\n\nTransformando imagenes...")

    # for y in range(len(imagenes)):
        nombre_imagen = nombres_imagenes[indice]

        # ImagenRotada90 = rotacion_imagen(paths_imagenes[indice], 90)
        # ImagenRotada90.save(f"{path}/Imagenes/r90_{nombre_imagen}")

        # ImagenRotada180 = rotacion_imagen(paths_imagenes[indice], 180)
        # ImagenRotada180.save(f"{path}/Imagenes/r180_{nombre_imagen}")

        # ImagenRotada270 = rotacion_imagen(paths_imagenes[indice], 270)
        # ImagenRotada270.save(f"{path}/Imagenes/r270_{nombre_imagen}")

        ImagenInvertida = invertir_imagen(imagenes[indice])
        cv2.imwrite(f"{path}/Imagenes/Inv_{nombre_imagen}", ImagenInvertida)

        # ImagenRotada90Inv = rotacion_imagen(
        #     f"{path}/Imagenes/Inv_{nombre_imagen}", 90)
        # ImagenRotada90Inv.save(f"{path}/Imagenes/Inv_r90_{nombre_imagen}")

        # ImagenRotada180Inv = rotacion_imagen(
        #     f"{path}/Imagenes/Inv_{nombre_imagen}", 180)
        # ImagenRotada180Inv.save(f"{path}/Imagenes/Inv_r180_{nombre_imagen}")

        # ImagenRotada270Inv = rotacion_imagen(
        #     f"{path}/Imagenes/Inv_{nombre_imagen}", 270)
        # ImagenRotada270Inv.save(f"{path}/Imagenes/Inv_r270_{nombre_imagen}")

        # new_anottation(anotaciones[indice], imagenes[indice], 90,
        #                'ROT', f'{path}/Anotaciones/r90_{nombre_anotacion}')
        # new_anottation(anotaciones[indice], imagenes[indice], 180,
        #                'ROT', f'{path}/Anotaciones/r180_{nombre_anotacion}')
        # new_anottation(anotaciones[indice], imagenes[indice], 270,
        #                'ROT', f'{path}/Anotaciones/r270_{nombre_anotacion}')
        new_anottation(anotaciones[indice], imagenes[indice], 270,
                       'INV', f'{path}/Anotaciones/Inv_{nombre_anotacion}')
        # new_anottation(anotaciones[indice], imagenes[indice], 90,
        #                'INV_ROT', f'{path}/Anotaciones/Inv_r90_{nombre_anotacion}')
        # new_anottation(anotaciones[indice], imagenes[indice], 180,
        #                'INV_ROT', f'{path}/Anotaciones/Inv_r180_{nombre_anotacion}')
        # new_anottation(anotaciones[indice], imagenes[indice], 270,
        #                'INV_ROT', f'{path}/Anotaciones/Inv_r270_{nombre_anotacion}')

    print(f"\n\nNuevas imagenes y anotaciones creadas!")


# ______________________________________________________________________________________________________________________
# AUMENTO DEL DATASET


imagenes, nombres_imagenes, anotaciones, nombres_anotaciones, paths_imagenes = lectura_imagenes_anotaciones(
    dir_train)
realiza_aumento_dataset(imagenes, nombres_imagenes,
                        anotaciones, nombres_anotaciones, dir_train, paths_imagenes)

imagenes, nombres_imagenes, anotaciones, nombres_anotaciones, paths_imagenes = lectura_imagenes_anotaciones(
    dir_val)
realiza_aumento_dataset(imagenes, nombres_imagenes,
                        anotaciones, nombres_anotaciones, dir_val, paths_imagenes)
