'''
    SE TIENE QUE EJECUTAR ESTE SCRIPT EN LA CARPETA QUE CONTIENE LAS DISTINTAS CLASES

'''
import sys
import cv2
import os
import glob
import PIL


dir_train = './dataset/dataset-clasificacion-tipos-ampollas/ToDrive/train'
dir_val = './dataset/dataset-clasificacion-tipos-ampollas/ToDrive/val'

# ______________________________________________________________________________________________________________________
# FUNCION ROTACION


def rotacion(img_path, rt_degr):
    img = Image.open(img_path)

    return img.rotate(rt_degr, expand=1)


# ______________________________________________________________________________________________________________________
# FUNCION INVERTIR
def invertir(imagen):

    ImagenInvertida = cv2.flip(imagen, 1)  # 1: Eje Vertical - 0:Eje horizontal

    return ImagenInvertida

# ______________________________________________________________________________________________________________________
# LECTURA DE ARCHIVOS EN CARPETA

# Obtenemos la ruta desde donde se ejecuta nuestro script


def aplica_transformaciones(directorio):
    # Buscamos las carpetas de carpetas
    clases = os.listdir(directorio)

    # El archivo de la lista de carpetas ".py", lo quitamos de la lista
    clases = [x for x in clases if "." not in x]
    # print("\n\nCLASES EXISTENTES:")
    # print(clases)

    # Obtenemos las rutas de las distintas carpetas
    paths = []
    for i in range(len(clases)):
        paths.append(os.path.join(directorio, clases[i]))

    # Vemos la cantidad de archivos de cada clase
    # print("\n\nCANTIDAD DE IMAGENES EN CADA CLASE:")
    for x in range(len(clases)):
        cantidad_imagenes = os.listdir(paths[x])
        # print(f"Clase '{clases[x]}': {len(cantidad_imagenes)} imágenes")

    # ______________________________________________________________________________________________________________________
    # APLICAMOS LA ROTACION:

    # Recorremos cada clase y aplicamos la transformacion sobre cada imagen:
    print('\n')
    for x in range(len(clases)):
        imagenes = [cv2.imread(file)
                    for file in glob.glob(f"{paths[x]}/*.png")]
        print(f"Transformando imagenes de la clase {clases[x]}...")

        paths_imagenes = glob.glob(f"{paths[x]}/*.png")

        for y in range(len(imagenes)):

            nombres_imagenes = os.listdir(paths[x])
            nombre_imagen = nombres_imagenes[y]
            path_imagen = paths_imagenes[y]

            # ImagenRotada90 = rotacion_imagen(path_imagen, 90)
            # ImagenRotada90.save(f"{path_imagen}/r90_{nombre_imagen}")

            ImagenInvertida = invertir(imagenes[y])
            # ImagenRotada90Inv = rotacion(ImagenInvertida, 90, None, 1.0)
            # ImagenRotada180Inv = rotacion(ImagenInvertida, 180, None, 1.0)
            # ImagenRotada270Inv = rotacion(ImagenInvertida, 270, None, 1.0)
            # cv2.imwrite(f"{paths[x]}/r90_{nombre_imagen}", ImagenRotada90)
            # cv2.imwrite(f"{paths[x]}/r180_{nombre_imagen}", ImagenRotada180)
            # cv2.imwrite(f"{paths[x]}/r270_{nombre_imagen}", ImagenRotada270)
            cv2.imwrite(f"{paths[x]}/Inv_{nombre_imagen}", ImagenInvertida)
            # cv2.imwrite(f"{paths[x]}/Inv_r90_{nombre_imagen}", ImagenRotada90Inv)
            # cv2.imwrite(f"{paths[x]}/Inv_r180_{nombre_imagen}", ImagenRotada180Inv)
            # cv2.imwrite(f"{paths[x]}/Inv_r270_{nombre_imagen}", ImagenRotada270Inv)

    print("\n\nCANTIDAD DE IMAGENES EN CADA CLASE:")
    for x in range(len(clases)):
        cantidad_imagenes = os.listdir(paths[x])
        print(f"Clase '{clases[x]}': {len(cantidad_imagenes)} imágenes")


aplica_transformaciones(dir_train)
aplica_transformaciones(dir_val)
