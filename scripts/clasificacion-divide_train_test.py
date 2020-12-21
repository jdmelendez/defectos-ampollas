'''

ESTE SCRIPT DEBE EJECUTARSE EN UN DIRECTORIO QUE CONTENGA LAS DISTINTAS CLASES

'''


# LIBRERIAS:
import sys
import shutil
import random
import numpy as np
import os
# from clasificacion_main import BLISTERS, AMPOLLAS

BLISTERS = 1
AMPOLLAS = 0

TRAIN_SPLIT = 0.9  # TODO Tamaño del dataset de "training" (sobre 1)
seed = 5  # Semilla de aletoriedad


# Obtenemos la ruta desde donde se alojara el dataset de clasificacion
if BLISTERS:
    dir_clasificacion = './dataset/dataset-clasificacion-blisters'

if AMPOLLAS:
    dir_clasificacion = './dataset/dataset-clasificacion-ampollas'


seed = 5  # TODO Semilla de aletoriedad

# Creamos la carpeta donde se almacenara el conjunto de entrenamiento y test
try:
    print("\nCreando carpeta ToDrive...")

    os.mkdir(os.path.join(dir_clasificacion, 'ToDrive'))

except FileExistsError:
    print('Las carpeta ToDrive ya estaba creada.' + "\n")

# Obtenemos las distintas clases del dataset (cada clase es una carpeta)
clases = os.listdir(dir_clasificacion)

# El archivo de la lista de carpetas ".py", lo quitamos de la lista
clases = [x for x in clases if "ToDrive" not in x]
print("\n\nCLASES EXISTENTES:\n")
for clase in clases:
    print(f"{clase}")

# Creacion de carpetas:
train_dir = os.path.join(dir_clasificacion, 'ToDrive/train')
test_dir = os.path.join(dir_clasificacion, 'ToDrive/test')

train_dir_clases = []
test_dir_clases = []

for i in range(len(clases)):
    train_dir_clases.append(os.path.join(train_dir, clases[i]))
    test_dir_clases.append(os.path.join(test_dir, clases[i]))

try:
    print("\nCreando directorios de train y test...")
    # Se crean las carpetas de train y test
    os.mkdir(train_dir)
    os.mkdir(test_dir)

    # Se crean las carpetas de cada clase
    for i in range(len(test_dir_clases)):
        os.mkdir(train_dir_clases[i])
        os.mkdir(test_dir_clases[i])

except FileExistsError:
    print('Las carpetas ya han sido creadas.' + "\n")

# Listamos las rutas de cada clase
dir_clases = []
for i in range(len(clases)):
    dir_clases.append(os.path.join(dir_clasificacion, clases[i]))


# Recopilación de imagenes en cada clase:
files_clases = []
for i in range(len(clases)):
    files_clases.append([os.path.join(dir_clases[i], f) for f in os.listdir(
        dir_clases[i]) if os.path.isfile(os.path.join(dir_clases[i], f))])

# Split de separación de training

msk_clases = []
for i in range(len(clases)):
    for j in range(len(files_clases[i])):
        random.seed(seed)
        msk_clases.append(np.random.rand(len(files_clases[i])) < TRAIN_SPLIT)

rand_items_clases = []
for i in range(len(clases)):
    random.seed(seed)
    rand_items_clases.append(random.sample(
        files_clases[i], int(len(files_clases[i]) * TRAIN_SPLIT)))


# Funcion para mover imagenes desde carpetas origen a "train" y "valid"
def move_file_list(directory, file_list):
    for f in file_list:
        f_name = f.split('/')[-1]
        shutil.move(f, directory)


# LLamada a la función:
for i in range(len(clases)):
    move_file_list(train_dir_clases[i], rand_items_clases[i])

files_clases_test = []
# Imagenes que quedan en la carpeta original para test:
for i in range(len(clases)):
    files_clases_test.append([os.path.join(dir_clases[i], f)
                              for f in os.listdir(dir_clases[i])
                              if os.path.isfile(os.path.join(dir_clases[i], f))])


# LLamada a la función:
for i in range(len(clases)):
    move_file_list(test_dir_clases[i], files_clases_test[i])

# Eliminacion de carpetas vacias:
# for i in dir_clases:
#     os.rmdir(i)

print("Division en TRAIN y TEST...FINALIZADA!")
