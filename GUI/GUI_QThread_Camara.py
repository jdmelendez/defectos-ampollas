import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage
# from GUI_crea_mensaje_alerta import crea_mensaje_alerta
from GUI_config import ANCHO_IMAGEN, ALTO_IMAGEN


class ActivaCamara(QtCore.QThread):
    envio_imagen = QtCore.pyqtSignal(QImage)
    envio_imagen_capturar = QtCore.pyqtSignal(QImage)
    #placaRecortada = QtCore.pyqtSignal(QImage)

    # def rescale_frame(self,frame, percent=75):
    #     width = int(frame.shape[1] * percent / 100)
    #     height = int(frame.shape[0] * percent / 100)
    #     dim = (width, height)
    #     return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    def run(self):
        self.cap = cv2.VideoCapture(0)
        # self.cap.set(3, ALTO_IMAGEN)
        # self.cap.set(4, ANCHO_IMAGEN)

        # self.width_cap = cap.get(3)  # float
        # self.height_cap = cap.get(4)  # float
        # print(self.width_cap,self.height_cap)

        self.contador_no_circulos = 0
        self.circulo_encontrado = 0

        while True:
            ret, frame = self.cap.read()

            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # self.findCircles(rgbImage)
                # time.sleep(1)

                if self.circulo_encontrado == 1:
                    rgbImage = cv2.cvtColor(
                        self.frame_recortado, cv2.COLOR_BGR2RGB)
                    self.imagen_camara_emit = QImage(
                        rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)

                else:
                    imagen_camara = QImage(
                        rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                    self.imagen_camara_emit = imagen_camara.scaled(
                        ANCHO_IMAGEN, ALTO_IMAGEN, QtCore.Qt.KeepAspectRatio)

                self.envio_imagen.emit(self.imagen_camara_emit)
                self.envio_imagen_capturar.emit(self.imagen_camara_emit)

    def stop(self):
        try:
            self.cap.release()
            self.terminate()
        except:
            texto = "Ten paciencia. Has pulsado dos veces. Vuelve a pulsar para reconfigurar el boton"
            crea_mensaje_alerta(texto)
