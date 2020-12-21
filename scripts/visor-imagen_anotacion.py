import math
from matplotlib import patches
import matplotlib.pyplot as plt
import matplotlib
import xml.etree.cElementTree as ET
import pandas as pd
import numpy as np
import csv
import io
import glob
import os
import cv2

Anotaciones = os.listdir(
    './dataset/dataset-deteccion-defectos-ampollas/ToDrive/train/Anotaciones')
Imagenes = os.listdir(
    './dataset/dataset-deteccion-defectos-ampollas/ToDrive/train/Imagenes')
# Anotaciones = os.listdir(
#     './dataset/dataset-deteccion/ToDrive/train/Anotaciones')
# Imagenes = os.listdir('./dataset/dataset-deteccion/ToDrive/train/Imagenes')

for indice in range(len(Imagenes)):
    nombre = Imagenes[indice][:-4]
    # nombre = "r180_201110_1264_13"

    '''
        r90_
        r180_
        r270_
        Inv_
        Inv_r90_
        Inv_r180_
        Inv_r270_
        '''

    DICCIONARIO_COLORES_DEFECTOS = {"sin_defecto": 'black',
                                    "blis_imp": 'purple',
                                    "amp_imp": 'orange',
                                    "amp_morf_cabeza": 'blue',
                                    "amp_morf_cuello": 'green',
                                    "babe_bicalm": 'green',
                                    "babe_vitaminC": 'green',
                                    "babe_proteos2f": 'green'}
    # ": 'red',
    # "amp_dim": 'yellow'}

    path_annotation_xml = f"./dataset/dataset-deteccion-defectos-ampollas/ToDrive/train/Anotaciones/{nombre}.xml"
    annotation_xml = ET.parse(path_annotation_xml)
    root = annotation_xml.getroot()

    header = ["xmin", "ymin", "xmax", "ymax"]

    image = plt.imread(
        f"./dataset/dataset-deteccion-defectos-ampollas/ToDrive/train/Imagenes/{nombre}.png")
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], xticks=[], yticks=[])
    plt.imshow(image)

    print(f"\n-----------------\n{nombre}\n")

    for i in root:
        for child in i:

            label = child.tag
            color = DICCIONARIO_COLORES_DEFECTOS[label]
            data_string = child.text

            if data_string == '-':
                continue

            else:
                data = io.StringIO(data_string.strip())
                df = pd.read_csv(data, sep=",", header=None,
                                 names=header, lineterminator=";")
                # print(df)

                for index, row in df.iterrows():

                    xmin = int(row['xmin'])
                    ymin = int(row['ymin'])
                    xmax = int(row['xmax'])
                    ymax = int(row['ymax'])
                    width = xmax - xmin
                    heigth = ymax - ymin

                    rect = patches.Rectangle((xmin, ymin), width, heigth,
                                             edgecolor=color, facecolor='none', linewidth=1.5)
                    ax.annotate(f"{label}", (xmin+3, ymin-5+(ymax-ymin)),
                                backgroundcolor=color, color='w', fontsize=5)
                    ax.add_patch(rect)

    plt.show()
    # plt.waitforbuttonpress(0)
