# "SIN DEFECTO": 0
# "BLISTER DEFECTUOSO": 1
# "BLISTER INCOMPLETO": 2
# "SELLADO AMPOLLA": 3
# "SOLIDOS AMPOLLA": 4
# "SERIGRAFIA AMPOLLA": 5
# "DIMENSION AMPOLLA":  6


"""
Se cogen las imagenes de la carpeta del dataset original y se organizan en carpetas
segun el defecto que tengan los blisters
"""
import sys
import os
import cv2
import glob
# from clasificacion_main import BLISTERS, AMPOLLAS

BLISTERS = 1
AMPOLLAS = 0

if BLISTERS:
    path_futuro = './dataset/dataset-clasificacion-blisters'
    PATH_IMGS = './dataset/dataset-original-blisters/Imagenes'

if AMPOLLAS:
    path_futuro = './dataset/dataset-clasificacion-ampollas'
    PATH_IMGS = './dataset/dataset-original-ampollas/Imagenes'


PATH_IMGS_SIN_DEFECTO = f'{path_futuro}/sin-defecto'
PATH_IMGS_BLIS_INCOMPLETO = f'{path_futuro}/blister-incompleto'
PATH_IMGS_BLIS_DEFECTUOSO = f'{path_futuro}/blister-defectuoso'
PATH_IMGS_AMP_SELLADO = f'{path_futuro}/ampolla-sellado'
PATH_IMGS_AMP_DIMENSION = f'{path_futuro}/ampolla-dimension'
PATH_IMGS_AMP_SERIGRAFIA = f'{path_futuro}/ampolla-serigrafia'
PATH_IMGS_AMP_SOLIDOS = f'{path_futuro}/ampolla-solidos'

DICCIONARIO_IDDEFECTO_PATHS = {"0": PATH_IMGS_SIN_DEFECTO,
                               "2": PATH_IMGS_BLIS_INCOMPLETO,
                               "1": PATH_IMGS_BLIS_DEFECTUOSO,
                               "3": PATH_IMGS_AMP_SELLADO,
                               "4": PATH_IMGS_AMP_SOLIDOS,
                               "5": PATH_IMGS_AMP_SERIGRAFIA,
                               "6": PATH_IMGS_AMP_DIMENSION}


def obtener_paths_imagenes(path=PATH_IMGS):
    paths_imagenes = glob.glob(f"{path}/*.png")
    return paths_imagenes


def obten_tipo_defecto(path_imagen):
    nombre_imagen = path_imagen.split('\\')[-1]
    tipo_defecto = nombre_imagen.split("_")[2]

    return tipo_defecto, nombre_imagen


def copiar_imagen_segun_defecto(path_imagen, tipo_defecto, nombre_imagen, diccionario=DICCIONARIO_IDDEFECTO_PATHS):

    for i in tipo_defecto:
        # if i == '3' or i == '4' or i=='5' or i=='6':
        #     continue
        path_imagen_clasificada = diccionario[i]
        imagen = cv2.imread(path_imagen)
        cv2.imwrite(f"{path_imagen_clasificada}/{nombre_imagen}", imagen)


paths_imagenes = obtener_paths_imagenes()

for path_imagen in paths_imagenes:
    tipo_defecto, nombre_imagen = obten_tipo_defecto(path_imagen)
    copiar_imagen_segun_defecto(path_imagen, tipo_defecto, nombre_imagen)
