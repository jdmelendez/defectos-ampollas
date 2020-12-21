"""
A traves de este script se realizan las siguientes funciones:

    1. Lectura del dataset-original, copia de los ficheros, y division en 'train' y 'test' dentro
       de una carpeta llamada 'ToDrive'. Para dividir el conjunto se ha de tener en cuenta que en los ficheros
       de test, se tenga el blister formado por la imagen de las dos camaras.   
    2. Aumento de la cantidad de imagenes del conjunto de 'train' y de 'test' mediante volteos y simetrias. 

    # pyinstaller --onefile --name Deteccion-Dataset dataset/scripts/deteccion-main.py


"""

from subprocess import Popen, call
import time


call('python ./dataset/scripts/deteccion-divide_train_test.py')
call('python ./dataset/scripts/deteccion-recorta_ampollas.py')
call('python ./dataset/scripts/deteccion-aumenta_train_test.py')
