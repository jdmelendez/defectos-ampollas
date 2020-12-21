from GUI_config import PATH_IMGS_TEMPORAL
import glob
import os

def elimina_imagen_temporal(path = PATH_IMGS_TEMPORAL):
    path_imagen = glob.glob(f"{path}/*.jpg")

    for imagen in path_imagen:
        try:
            os.remove(imagen)
        except:
            print("Error: No hay imagenes en la carpeta temporal")