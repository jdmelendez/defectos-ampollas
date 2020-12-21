from GUI_config import PATH_IMGS, PATH_IMGS_PINTADAS, PATH_ANNS, ALTO_IMAGEN, ANCHO_IMAGEN
from GUI_crea_xml import crea_xml
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
import cv2
import datetime


def guarda_imagen_y_anotacion(imagen_pintada, imagen_original, DICC_COORDENADAS_DEFECTOS_AUX, DICC_COORDENADAS_PRODUCTOS_AUX, imagen_pintada2, imagen_original2, DICC_COORDENADAS_DEFECTOS_AUX2, DICC_COORDENADAS_PRODUCTOS_AUX2, nombre_cliente, path_imgs=PATH_IMGS, path_imgs_pintadas=PATH_IMGS_PINTADAS, path_anns=PATH_ANNS):

    nombre = forma_nombre_ficheros(
        DICC_COORDENADAS_DEFECTOS_AUX)+f"_{nombre_cliente}"+"_I"
    nombre2 = forma_nombre_ficheros(
        DICC_COORDENADAS_DEFECTOS_AUX2)+f"_{nombre_cliente}"+"_D"

    guarda_imagen(imagen_pintada, imagen_original,
                  path_imgs, path_imgs_pintadas, nombre)
    guarda_anotacion(DICC_COORDENADAS_DEFECTOS_AUX,
                     DICC_COORDENADAS_PRODUCTOS_AUX, path_anns, nombre)

    guarda_imagen(imagen_pintada2, imagen_original2,
                  path_imgs, path_imgs_pintadas, nombre2)
    guarda_anotacion(DICC_COORDENADAS_DEFECTOS_AUX2,
                     DICC_COORDENADAS_PRODUCTOS_AUX2, path_anns, nombre2)


def guarda_imagen(imagen_pintada, imagen_original, path_imgs, path_imgs_pintadas, nombre):

    imagen_original.save(f"{path_imgs}/{nombre}.png")

    imagen_pintada_escalada = imagen_pintada.scaled(
        ANCHO_IMAGEN, ALTO_IMAGEN, QtCore.Qt.KeepAspectRatio)
    imagen_pintada_escalada.save(f"{path_imgs_pintadas}/{nombre}.png")


def guarda_anotacion(DICC_COORDENADAS_DEFECTOS_AUX, DICC_COORDENADAS_PRODUCTOS_AUX, path_anns, nombre):

    xml_defectos = crea_xml(DICC_COORDENADAS_DEFECTOS_AUX, label='defectos')
    xml_productos = crea_xml(DICC_COORDENADAS_PRODUCTOS_AUX, label='productos')
    fichero_xml = open(f"{path_anns}/{nombre}.xml", "a")
    fichero_xml.write('<label>\n')
    fichero_xml.write(str(xml_defectos))
    fichero_xml.write('\n')
    fichero_xml.write(str(xml_productos))
    fichero_xml.write('\n')
    fichero_xml.write('</label>')
    fichero_xml.close()


def forma_nombre_ficheros(DICC_COORDENADAS_DEFECTOS_AUX):
    existe_defecto = 0
    nombre_tipo_defecto = 'C'
    for valores in DICC_COORDENADAS_DEFECTOS_AUX.values():
        if valores[1] != '-':
            nombre_tipo_defecto = nombre_tipo_defecto + str(valores[2])
            existe_defecto = 1

    if existe_defecto == 0:
        nombre_tipo_defecto = 'C0'
        DICC_COORDENADAS_DEFECTOS_AUX['SIN DEFECTO'][1] = [
            [0, 0, ANCHO_IMAGEN, ALTO_IMAGEN]]

    ahora = datetime.datetime.now()
    nombre = f"{(ahora.year)//10%10}{(ahora.year) % 10}{ahora.month}{ahora.day}_{ahora.hour}{ahora.minute}{ahora.second}_{nombre_tipo_defecto}"

    return nombre
