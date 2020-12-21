import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage
from GUI_crea_mensaje_alerta import crea_mensaje_alerta
from GUI_config import PATH_IMGS_TEMPORAL, ANCHO_IMAGEN, ALTO_IMAGEN
import glob
import time


class DetectaImagen(QtCore.QThread):
    # envio_imagen = QtCore.pyqtSignal(QImage)
    envio_imagen = QtCore.pyqtSignal(bool)

    def run(self):

        path_imagen = []
        existe_imagen = 0
        cantidad_imagenes = 0
        while cantidad_imagenes < 2:
            time.sleep(1)
            path_imagen = glob.glob(f"{PATH_IMGS_TEMPORAL}/*.jpg")
            cantidad_imagenes = len(path_imagen)

        existe_imagen = 1
        cantidad_imagenes = 0
        self.envio_imagen.emit(existe_imagen)

        # try:
        #     imagen = cv2.imread(path_imagen[0])
        #     rgbImage = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        #     # time.sleep(5)
        #     imagen = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)

        #     # self.imagen_temp_emit = imagen.scaled(ANCHO_IMAGEN, ALTO_IMAGEN, QtCore.Qt.KeepAspectRatio)

        #     self.envio_imagen.emit(imagen)
        #     path_imagen=[]
        # except:
        #     print("Espera un poco")
        #     path_imagen = []

    def stop(self):
        try:
            self.terminate()
        except:
            texto = "Ten paciencia. Has pulsado dos veces. Vuelve a pulsar para reconfigurar el boton"
            crea_mensaje_alerta(texto)
