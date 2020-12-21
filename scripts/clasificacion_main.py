"""
A traves de este script se realizan las siguientes funciones:

    1. Lectura del dataset-original y distribucion de las imagenes en el dataset-clasificacion
       segun el identificador en el nombre de la imagen.
    2. Division del dataset-clasificacion en 'train' y 'test', ubicado en una carpeta llamada 'ToDrive'
       dentro del dataset-clasificacion.
    3. Una vez dividido el conjunto, se balancean las clases, de manera que las clases que contienen
       imagenes de mas con respecto al minimo de imagenes contenidas en una clase, se derivan a 
       al conjunto de 'test'.
    4. Aumento de la cantidad de imagenes del conjunto de 'train' y de 'test' mediante volteos y simetrias. 

    # pyinstaller --onefile --name Clasificacion-Dataset dataset/scripts/clasificacion-main.py


"""

from subprocess import Popen, call
import time


BLISTERS = 1
AMPOLLAS = 0

if AMPOLLAS:
    call('python ./dataset/scripts/deteccion-recorta-ampollas.py')

call('python ./dataset/scripts/clasificacion-distribuye_imagenes.py')
call('python ./dataset/scripts/clasificacion-divide_train_test.py')
# call('python ./dataset/scripts/clasificacion-balancea_train_test.py')
