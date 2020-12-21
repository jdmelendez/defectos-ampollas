
# LIBRERIAS:

import shutil
import random
import numpy as np
import os
import glob

train_split = 0.8  # TODO Tamaño del dataset de "training" (sobre 1)
valid_split = 0.2  # TODO Tamaño del dataset de "training" (sobre 1)
seed = 5  # Semilla de aletoriedad

# Obtenemos la ruta desde donde se alojara el dataset de clasificacion
dir_original = './dataset/dataset-clasificacion-tipos-ampollas'


# Elegir tipo de analisis
tipos_ampollas = os.listdir(dir_original)
paths_tipos_ampollas = []

print("\nELIGE TIPO DE ANALISIS:")
for indice, tipo in enumerate(tipos_ampollas):
    print(f"{indice+1} --> {tipo}")
    paths_tipos_ampollas.append(os.path.join(dir_original, tipo))

menu1 = int(
    input("\nIntroduce el tipo de ampolla con el que deseas trabajar (numero):"))
tipos_ampollas_elegido = tipos_ampollas[menu1 - 1]
dir_tipos_ampollas_elegido = os.path.join(dir_original, tipos_ampollas_elegido)

# Creamos la carpeta donde se almacenara el conjunto de entrenamiento y test, y las clases SI y NO
try:
    print("\nCreando carpeta ToDrive...")

    os.mkdir(os.path.join(dir_original, 'ToDrive'))
    os.mkdir(os.path.join(dir_original, 'ToDrive/SI'))
    os.mkdir(os.path.join(dir_original, 'ToDrive/NO'))

except FileExistsError:
    print('Las carpetas ToDrive ya estaba creada.' + "\n")


# Recolectamos imagenes para las carpetas de SI y NO, siendo la de NO rellenada por imagenes del resto clases
cantidad_imagenes_tipo_ampolla_elegido = len(
    glob.glob(f'{dir_tipos_ampollas_elegido}/*.png'))
cantidad_imagenes_a_escoger_por_clase = cantidad_imagenes_tipo_ampolla_elegido / \
    len(tipos_ampollas)

for imagen in glob.glob(f'{dir_tipos_ampollas_elegido}/*.png'):
    shutil.copy(imagen, os.path.join(dir_original, 'ToDrive/SI'))

cantidad_de_archivos_copiados_a_NO = 0

while (cantidad_de_archivos_copiados_a_NO < cantidad_imagenes_tipo_ampolla_elegido):
    for tipo_ampolla in paths_tipos_ampollas:

        if tipo_ampolla == dir_tipos_ampollas_elegido:
            continue

        for i in range(int(cantidad_imagenes_a_escoger_por_clase)):
            if cantidad_de_archivos_copiados_a_NO < cantidad_imagenes_tipo_ampolla_elegido:
                try:
                    archivo_elegido_no_existe = 0
                    while archivo_elegido_no_existe == 0:

                        archivo_elegido = random.choice(
                            os.listdir(tipo_ampolla))

                        if archivo_elegido not in os.listdir(os.path.join(dir_original, 'ToDrive/NO')):
                            archivo_elegido_no_existe = 1

                    shutil.copy(os.path.join(tipo_ampolla, archivo_elegido),
                                os.path.join(dir_original, 'ToDrive/NO'))
                    cantidad_de_archivos_copiados_a_NO += 1
                except:
                    print(f'No existen imagenes de la clase {tipo_ampolla}')


# Obtenemos las distintas clases del dataset (cada clase es una carpeta)
carpetas = os.listdir(os.path.join(dir_original, 'ToDrive'))

# El archivo de la lista de carpetas ".py", lo quitamos de la lista
carpetas = [x for x in carpetas if "ToDrive" not in x]
print("\n\nCLASES EXISTENTES:\n")
print(carpetas)

# Creacion de carpetas:
train_dir = os.path.join(dir_original, 'ToDrive/train')
val_dir = os.path.join(dir_original, 'ToDrive/val')
test_dir = os.path.join(dir_original, 'ToDrive/test')

train_dir_carpetas = []
val_dir_carpetas = []
test_dir_carpetas = []

for i in range(len(carpetas)):
    train_dir_carpetas.append(os.path.join(train_dir, carpetas[i]))
    test_dir_carpetas.append(os.path.join(test_dir, carpetas[i]))
    val_dir_carpetas.append(os.path.join(val_dir, carpetas[i]))

try:
    print("\n" + "Creando carpetas...")
    # Train:
    os.mkdir(train_dir)
    os.mkdir(test_dir)
    os.mkdir(val_dir)

    for i in range(len(test_dir_carpetas)):
        os.mkdir(train_dir_carpetas[i])
        os.mkdir(test_dir_carpetas[i])
        os.mkdir(val_dir_carpetas[i])

except FileExistsError:
    print('Las carpetas ya existen.' + "\n")

dir_carpetas = []
for i in range(len(carpetas)):
    dir_carpetas.append(os.path.join(dir_original, f'ToDrive/{carpetas[i]}'))


# Recopilación de archivos de carpetas originales:
files_carpetas = []
for i in range(len(carpetas)):
    files_carpetas.append([os.path.join(dir_carpetas[i], f) for f in os.listdir(
        dir_carpetas[i]) if os.path.isfile(os.path.join(dir_carpetas[i], f))])


# Split de separación de training
nombres_archivos = []
nombres_archivos_random_train = []
nombres_archivos_random_valid = []

# TODO : Dividir los conjuntos para que las imagenes de la camara D e I vayan siempre juntas
for i in range(len(carpetas)):
    # nombres_archivos.append(os.listdir(dir_carpetas[i]))
    random.seed(seed)
    nombres_archivos_random_train.append(random.sample(
        files_carpetas[i], k=int(len(files_carpetas[i])*train_split)))

for i in range(len(carpetas)):
    # nombres_archivos_random_train.append(os.listdir(dir_carpetas[i]))
    random.seed(seed)
    nombres_archivos_random_valid.append(random.sample(
        nombres_archivos_random_train[i], k=int(len(files_carpetas[i])*valid_split)))

for i in range(len(carpetas)):
    for archivo in nombres_archivos_random_valid[i]:
        nombres_archivos_random_train[i].remove(archivo)


# Añadir nombres arhivos random a la ruta correspondiente:
lista_images_train = []
lista_images_valid = []

for i in range(len(carpetas)):
    for j in range(len(nombres_archivos_random_train[i])):
        lista_images_train.append(os.path.join(
            dir_carpetas[i], nombres_archivos_random_train[i][j]))

for i in range(len(carpetas)):
    for j in range(len(nombres_archivos_random_valid[i])):
        lista_images_valid.append(os.path.join(
            dir_carpetas[i], nombres_archivos_random_valid[i][j]))

# Funcion para mover imagenes desde carpetas origen a "train" , "valid" "test"


def move_file_list(directory, file_list):
    for f in file_list:
        f_name = f.split('/')[-1]
        try:
            shutil.move(f, directory)
        except:
            print("La imagen ya existe en el directorio de destino")


# LLamada a la función:
for i in range(len(carpetas)):
    move_file_list(train_dir_carpetas[i], nombres_archivos_random_train[i])
    move_file_list(val_dir_carpetas[i], nombres_archivos_random_valid[i])

files_clases_test = []

# Imagenes que quedan en la carpeta original para test:
for i in range(len(carpetas)):
    files_clases_test.append([os.path.join(dir_carpetas[i], f)
                              for f in os.listdir(dir_carpetas[i])
                              if os.path.isfile(os.path.join(dir_carpetas[i], f))])


# LLamada a la función:
for i in range(len(carpetas)):
    move_file_list(test_dir_carpetas[i], files_clases_test[i])

# Eliminacion de carpetas vacias:
for i in dir_carpetas:
    os.rmdir(i)

print("Division en TRAIN, VALID Y TEST...FINALIZADA!")
