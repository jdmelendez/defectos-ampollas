
import glob
import shutil
import random
import os
train_split = 0.8  # TODO Tamaño del dataset de "training" (sobre 1)
valid_split = 0.2  # TODO Tamaño del dataset de "training" (sobre 1)
seed = 5  # TODO Semilla de aletoriedad

# LIBRERIAS:


# Obtenemos la ruta desde donde se aloja el dataset-original
dir_original = './dataset/dataset-original-blisters'
# dir_deteccion = './dataset/dataset-deteccion-blisters'

# dir_original = './dataset/dataset-original-ampollas'
dir_deteccion = './dataset/dataset-deteccion-defectos-ampollas'

# Copiamos el dataset original en el la carpeta de dataset-deteccion para trabajar con el
carpetas_dir_original = os.listdir(dir_original)
for carpeta in carpetas_dir_original:
    try:
        os.mkdir(os.path.join(dir_deteccion, carpeta))
    except FileExistsError:
        print(f'La carpeta {carpeta} ya existe.' + "\n")

    ficheros_en_carpeta_original = os.listdir(
        os.path.join(dir_original, carpeta))

    for fichero in ficheros_en_carpeta_original:
        shutil.copy(os.path.join(
            dir_original, f"{carpeta}/{fichero}"), os.path.join(dir_deteccion, carpeta))

# Buscamos las carpetas dentro del dataset-deteccion
carpetas = os.listdir(dir_deteccion)

# Creamos la carpeta donde se almacenara el conjunto de entrenamiento y test
try:
    print("\nCreando carpeta ToDrive...")

    os.mkdir(os.path.join(dir_deteccion, 'ToDrive'))

except FileExistsError:
    print('Las carpeta ToDrive ya estaba creada.' + "\n")

# El archivo de la lista de carpetas ".py", lo quitamos de la lista
carpetas = [x for x in carpetas if "." not in x]
print("\n\nCARPETAS EXISTENTES:")
print(carpetas)

# Creacion de carpetas:
train_dir = os.path.join(dir_deteccion, 'ToDrive/train')
val_dir = os.path.join(dir_deteccion, 'ToDrive/val')
test_dir = os.path.join(dir_deteccion, 'ToDrive/test')

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
    dir_carpetas.append(os.path.join(dir_deteccion, carpetas[i]))


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
    nombres_archivos.append(os.listdir(dir_carpetas[i]))
    random.seed(seed)
    nombres_archivos_random_train.append(random.sample(
        nombres_archivos[i], k=int(len(nombres_archivos[i])*train_split)))

for i in range(len(carpetas)):
    # nombres_archivos_random_train.append(os.listdir(dir_carpetas[i]))
    random.seed(seed)
    nombres_archivos_random_valid.append(random.sample(
        nombres_archivos_random_train[i], k=int(len(nombres_archivos[i])*valid_split)))

for i in range(len(carpetas)):
    for archivo in nombres_archivos_random_valid[i]:
        nombres_archivos_random_train[i].remove(archivo)


# Añadir nombres arhivos random a la ruta correspondiente:
lista_annotations_train = []
lista_images_train = []
lista_annotations_valid = []
lista_images_valid = []

for j in range(len(nombres_archivos_random_train[0])):
    lista_annotations_train.append(os.path.join(
        dir_carpetas[0], nombres_archivos_random_train[0][j]))

for j in range(len(nombres_archivos_random_train[1])):
    lista_images_train.append(os.path.join(
        dir_carpetas[1], nombres_archivos_random_train[1][j]))

for j in range(len(nombres_archivos_random_valid[0])):
    lista_annotations_valid.append(os.path.join(
        dir_carpetas[0], nombres_archivos_random_valid[0][j]))

for j in range(len(nombres_archivos_random_valid[1])):
    lista_images_valid.append(os.path.join(
        dir_carpetas[1], nombres_archivos_random_valid[1][j]))

# Funcion para mover imagenes desde carpetas origen a "train" , "valid" "test"


def move_file_list(directory, file_list):
    for f in file_list:
        f_name = f.split('/')[-1]
        shutil.move(f, directory)


# LLamada a la función:
move_file_list(train_dir_carpetas[0], lista_annotations_train)
move_file_list(train_dir_carpetas[1], lista_images_train)
move_file_list(val_dir_carpetas[0], lista_annotations_valid)
move_file_list(val_dir_carpetas[1], lista_images_valid)

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
