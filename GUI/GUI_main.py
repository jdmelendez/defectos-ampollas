
# pyinstaller --windowed --icon=ampollas.ico --name Defectos-Ampollas --add-data="C:\Users\jmelendez\GIT\ampollas-control-calidad\GUI\icons;.\icons" --add-data="C:\Users\jmelendez\GIT\ampollas-control-calidad\GUI\InterfaceUI.ui;." --add-data="C:\Users\jmelendez\GIT\ampollas-control-calidad\GUI\ampollas.ico;." --add-data="C:\Users\jmelendez\GIT\ampollas-control-calidad\GUI\Archivos;." GUI_main.py

# Ejecutar la linea superior dentro de la carpeta GUI. Copiar despues la carpeta Archivos dentro de la carpeta donde esta el ejecutable. Si no funciona, cambiar de entorno.
# Si y esta todo creado .. pyinstaller Defectos-Ampollas.spec

# ================================================= LIBRERIAS ======================================================
import sys
import os
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QAction, QMessageBox, QFileSystemModel, QColumnView, QComboBox
from PyQt5.QtCore import QDir, QRect
from PyQt5.QtGui import QColor, QImage, QPixmap, QPen, QPainter, QFont, QStandardItemModel, QBrush
from pathlib import Path
import glob
import shutil
import copy
import time
import cv2


from GUI_config import PATH_IMGS, COLORES_DEFECTOS, DICCIONARIO_COORDENADAS_DEFECTOS, PATH_IMGS_TEMPORAL, DICCIONARIO_COORDENADAS_PRODUCTO
from GUI_comprueba_click_dentro_imagen import comprueba_click_dentro_imagen
from GUI_dibuja_region import dibuja_region
from GUI_guarda_imagen_y_anotacion import guarda_imagen_y_anotacion
from GUI_almacena_coordenadas_y_defecto import almacena_coordenadas_y_defecto
from GUI_almacena_coordenadas_y_producto import almacena_coordenadas_y_producto
from GUI_borrar_region import borrar_region
from GUI_crea_mensaje_alerta import crea_mensaje_alerta
from GUI_QThread_DetectaImagen import DetectaImagen
from GUI_elimina_imagen_temporal import elimina_imagen_temporal


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

 # ================================================= CARGA FICHERO UI ==================================================

        uifile = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'InterfaceUI.ui')
        uic.loadUi(uifile, self)

 # ================================================= INICIA BOTONES ====================================================

        # Botones tipo de defecto
        self.boton_def_morf_cabeza_amp.clicked.connect(
            lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_morf_cabeza_amp))
        self.boton_def_morf_cuello_amp.clicked.connect(
            lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_morf_cuello_amp))
        self.boton_def_imp_amp.clicked.connect(
            lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_imp_amp))
        self.boton_def_imp_blis.clicked.connect(
            lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_imp_blis))
        # self.boton_def_vaho.clicked.connect(
        #     lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_vaho))
        # # self.boton_def_no.clicked.connect(
        # #     lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_no))
        # # self.boton_def_no.clicked.connect(self.fn_boton_def_no)
        # self.boton_def_blister.clicked.connect(
        #     lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_blister))
        # self.boton_def_sucia.clicked.connect(
        #     lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_sucia))
        # self.boton_def_rotura.clicked.connect(
        #     lambda: self.obten_nombre_tipo_defecto(nombre_boton=self.boton_def_rotura))

        # Botones tipo de producto
        # self.comboBox_ampolla_error.currentIndexChanged.connect(
        #     self.fn_comboBox_ampolla_error)
        self.boton_ampolla_error.clicked.connect(
            self.fn_comboBox_ampolla_error)

        # self.comboBox_ampolla_error.

        # Botones edicion
        self.boton_lapiz.clicked.connect(self.fn_boton_lapiz)
        self.boton_borrar.clicked.connect(self.fn_boton_borrar)
        self.boton_validar.clicked.connect(self.fn_boton_validar)
        self.boton_cancelar.clicked.connect(self.fn_boton_cancelar)
        self.visor.mousePressEvent = self.mousePressEvent
        self.visor_2.mousePressEvent = self.mousePressEvent2
        self.dim_horizontal_spacer = 5
        self.FLAG_DIBUJAR = True
        self.FLAG_BORRAR = False
        self.FLAG_PRIMER_CLICK = True
        self.FLAG_SEGUNDO_CLICK = False

        # Camara
        self.FLAG_CAPTURA_IMAGEN = False
        self.FLAG_IMAGEN_CAPTURADA = False
        self.NUEVA_IMAGEN = True
        self.detecta_imagen()

        # Coordenadas defectos
        self.DICC_COORDENADAS_DEFECTOS_AUX = {}
        self.DICC_COORDENADAS_DEFECTOS_AUX2 = {}
        self.DICC_COORDENADAS_PRODUCTOS_AUX = {}
        self.DICC_COORDENADAS_PRODUCTOS_AUX2 = {}

        # Botones ventana
        finish = QAction("Quit", self)
        finish.triggered.connect(self.closeEvent)

 # ================================================= VISOR DE IMAGEN ==================================================

    def detecta_imagen(self):
        self.DetectaImagenQThread = DetectaImagen()
        self.DetectaImagenQThread.start()
        self.DetectaImagenQThread.envio_imagen.connect(
            self.recibeImagenTemporal)

    def recibeImagenTemporal(self, imagen_temporal_flag):
        """Recibe la imagen de la camara y la coloca en el visor, dependiendo de si hay una imagen colocada ya,
        o si se le ha dado la orden de capturar imagen

        Args:
            imagen_camara ([type]):variable pixelica proveniente del multihilo
        """
        if imagen_temporal_flag:
            path_imagen = glob.glob(f"{PATH_IMGS_TEMPORAL}/*.jpg")
            imagen = cv2.imread(path_imagen[0])
            imagen2 = cv2.imread(path_imagen[1])
            rgbImage = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            rgbImage2 = cv2.cvtColor(imagen2, cv2.COLOR_BGR2RGB)
            imagen = QImage(
                rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            imagen2 = QImage(
                rgbImage2.data, rgbImage2.shape[1], rgbImage2.shape[0], QImage.Format_RGB888)

            self.coloca_imagen_en_visor(
                imagen_camara1=imagen, imagen_camara2=imagen2)

            self.DICC_COORDENADAS_DEFECTOS_AUX = copy.deepcopy(
                DICCIONARIO_COORDENADAS_DEFECTOS)
            self.DICC_COORDENADAS_DEFECTOS_AUX2 = copy.deepcopy(
                DICCIONARIO_COORDENADAS_DEFECTOS)
            self.DICC_COORDENADAS_PRODUCTOS_AUX = copy.deepcopy(
                DICCIONARIO_COORDENADAS_PRODUCTO)
            self.DICC_COORDENADAS_PRODUCTOS_AUX2 = copy.deepcopy(
                DICCIONARIO_COORDENADAS_PRODUCTO)

            self.boton_validar.setEnabled(True)

        # if (self.FLAG_CAPTURA_IMAGEN == True) and (self.FLAG_IMAGEN_CAPTURADA == False):
            self.captura_imagen(imagen_camara1=imagen, imagen_camara2=imagen2)

    def coloca_imagen_en_visor(self, imagen_camara1, imagen_camara2, FLAG_BORRAR=False):
        """Recibe la imagen de la camra y la coloca en el visor. Ademas, calcula todos los parametros de escala,
        offsets, etc. """

        if FLAG_BORRAR:
            imagen_visor = imagen_camara1
            imagen_visor_2 = imagen_camara2

        else:
            imagen_visor = QPixmap.fromImage(imagen_camara1)
            imagen_visor_2 = QPixmap.fromImage(imagen_camara2)

        self.imagen_visor_escalada = imagen_visor.scaled(int(self.visor.width()), int(
            self.visor.height()), QtCore.Qt.KeepAspectRatio)
        self.imagen_visor_escalada2 = imagen_visor_2.scaled(int(self.visor_2.width()), int(
            self.visor_2.height()), QtCore.Qt.KeepAspectRatio)

        self.visor.setPixmap(self.imagen_visor_escalada)
        self.visor_2.setPixmap(self.imagen_visor_escalada2)
        # self.imagen_capturada = QPixmap.fromImage(imagen_camara)

        # Obtenemos las medidas del visor y de la imagen para despues poder comprobar si los click en modo edicion se efectuan dentro de la imagen
        ancho_imagen_visor = imagen_visor.width()
        alto_imagen_visor = imagen_visor.height()
        ancho_imagen_visor_escalada = self.imagen_visor_escalada.width()
        alto_imagen_visor_escalada = self.imagen_visor_escalada.height()
        ancho_visor = self.visor.width()
        alto_visor = self.visor.height()

        ancho_imagen_visor2 = imagen_visor_2.width()
        alto_imagen_visor2 = imagen_visor_2.height()
        ancho_imagen_visor_escalada2 = self.imagen_visor_escalada2.width()
        alto_imagen_visor_escalada2 = self.imagen_visor_escalada2.height()
        ancho_visor2 = self.visor_2.width()
        alto_visor2 = self.visor_2.height()

        self.ancho_zonaClick_imagen = [
            (ancho_visor-ancho_imagen_visor_escalada)/2, (ancho_visor-ancho_imagen_visor_escalada)/2+ancho_imagen_visor_escalada]
        self.alto_zonaClick_imagen = [
            (alto_visor-alto_imagen_visor_escalada)/2, (alto_visor-alto_imagen_visor_escalada)/2+alto_imagen_visor_escalada]
        self.offset_X = (ancho_visor - ancho_imagen_visor_escalada)/2
        self.offset_Y = (alto_visor - alto_imagen_visor_escalada) / 2
        self.factor_escala_dimension_x = ancho_imagen_visor_escalada/ancho_imagen_visor
        self.factor_escala_dimension_y = alto_imagen_visor_escalada / alto_imagen_visor

        self.ancho_zonaClick_imagen2 = [
            (ancho_visor2-ancho_imagen_visor_escalada2)/2, (ancho_visor2-ancho_imagen_visor_escalada2)/2+ancho_imagen_visor_escalada2]
        self.alto_zonaClick_imagen2 = [
            (alto_visor2-alto_imagen_visor_escalada2)/2, (alto_visor2-alto_imagen_visor_escalada2)/2+alto_imagen_visor_escalada2]
        self.offset_X2 = (ancho_visor2 - ancho_imagen_visor_escalada2)/2
        self.offset_Y2 = (alto_visor2 - alto_imagen_visor_escalada2) / 2
        self.factor_escala_dimension_x2 = ancho_imagen_visor_escalada2/ancho_imagen_visor2
        self.factor_escala_dimension_y2 = alto_imagen_visor_escalada2 / alto_imagen_visor2

    def captura_imagen(self, imagen_camara1, imagen_camara2):
        """Obtiene el frame y lo coloca en el visor"""
        self.imagen_capturada = QPixmap.fromImage(imagen_camara1)
        self.imagen_capturada2 = QPixmap.fromImage(imagen_camara2)
        self.coloca_imagen_en_visor(imagen_camara1, imagen_camara2)
        self.FLAG_IMAGEN_CAPTURADA = True

 # =========================================== TIPO DE DEFECTO SELECCIONADO ============================================
    def fn_comboBox_ampolla_error(self):
        self.id_tipo_defecto = 'AMPOLLA ERROR'  # Para obtener el color
        self.id_tipo_producto_error = self.comboBox_ampolla_error.currentText()
        self.FLAG_CAPTURA_IMAGEN = True
        self.FLAG_BORRAR = False
        self.FLAG_DIBUJAR = True
        self.FLAG_PRIMER_CLICK = True
        self.FLAG_SEGUNDO_CLICK = False
        self.DEFECTO_CLICK = False

    def obten_nombre_tipo_defecto(self, nombre_boton):
        """Al clicar cualquier boton de tipo de defecto, se obtiene el nombre del boton, y se activan una serie de flags
        que permiten dibuja en el lienzo y capturar la imagen del video"""
        self.id_tipo_defecto = nombre_boton.text()
        self.FLAG_CAPTURA_IMAGEN = True
        self.FLAG_BORRAR = False
        self.FLAG_DIBUJAR = True
        self.FLAG_PRIMER_CLICK = True
        self.FLAG_SEGUNDO_CLICK = False
        self.DEFECTO_CLICK = True

 # ================================================== LOCALIZA DEFECTO =================================================

    def fn_boton_lapiz(self):
        " Se activa el flag de dibujar y se desactiva el de borrar"
        self.FLAG_BORRAR = False
        self.FLAG_DIBUJAR = True

    def fn_boton_borrar(self):
        " Se activa el flag de borrar y se desactiva el de dibujar"
        self.FLAG_DIBUJAR = False
        self.FLAG_BORRAR = True

    def mousePressEvent(self, event):
        """Depende del flag activado, se dibuja o se borra. Se comprueba si el click se ha realizado dentro de la imagen,
        se ve el tipo de defecto seleccionado, y se dibuja de su respectivo color teniendo en cuenta los factores de
        escala.En el caso de borrar, se comrprueba que el click se ha realizado dentro de la region, se elimina esta,
        y se vuelve a dibujar el resto automaticamente"""

        if self.FLAG_DIBUJAR:

            if self.FLAG_PRIMER_CLICK:
                self.primer_click = self.visor.mapFromParent(event.pos())
                self.primer_click_x = self.primer_click.x()+self.dim_horizontal_spacer
                self.primer_click_y = self.primer_click.y()

                if comprueba_click_dentro_imagen(self.primer_click_x, self.primer_click_y, self.ancho_zonaClick_imagen, self.alto_zonaClick_imagen):

                    self.FLAG_PRIMER_CLICK = False
                    self.FLAG_SEGUNDO_CLICK = True

                else:
                    self.FLAG_PRIMER_CLICK = True
                    self.FLAG_SEGUNDO_CLICK = False

            elif self.FLAG_SEGUNDO_CLICK:
                try:
                    if self.DEFECTO_CLICK:
                        color = COLORES_DEFECTOS[self.id_tipo_defecto]
                    else:
                        color = 'black'

                    self.segundo_click = self.visor.mapFromParent(event.pos())
                    self.segundo_click_x = self.segundo_click.x()+self.dim_horizontal_spacer
                    self.segundo_click_y = self.segundo_click.y()

                    if comprueba_click_dentro_imagen(self.segundo_click_x, self.segundo_click_y, self.ancho_zonaClick_imagen, self.alto_zonaClick_imagen):

                        self.FLAG_PRIMER_CLICK = True
                        self.FLAG_SEGUNDO_CLICK = False

                        dibuja_region(QPainter(self.visor.pixmap()), self.primer_click_x, self.primer_click_y,
                                      self.segundo_click_x, self.segundo_click_y, color, 3, self.offset_X, self.offset_Y)

                        self.update()
                        self.visor.update()

                        if self.DEFECTO_CLICK:

                            self.COORDENADAS_DEFECTOS = [int(min([self.primer_click_x-self.offset_X, self.segundo_click_x-self.offset_X]) / self.factor_escala_dimension_x),
                                                         int(min([self.primer_click_y-self.offset_Y, self.segundo_click_y-self.offset_Y]
                                                                 ) / self.factor_escala_dimension_y),
                                                         int(max([self.primer_click_x-self.offset_X, self.segundo_click_x-self.offset_X]
                                                                 ) / self.factor_escala_dimension_x),
                                                         int(max([self.primer_click_y-self.offset_Y, self.segundo_click_y-self.offset_Y])/self.factor_escala_dimension_y)]

                            # Se va actualizando un diccionario que contiene las clases de los defectos y las coordenadas de cada una de las regiones

                            self.DICC_COORDENADAS_DEFECTOS_AUX = almacena_coordenadas_y_defecto(
                                self.COORDENADAS_DEFECTOS, self.id_tipo_defecto, self.DICC_COORDENADAS_DEFECTOS_AUX, flag_nueva_imagen=self.NUEVA_IMAGEN)

                        else:

                            self.COORDENADAS_PRODUCTOS = [int(min([self.primer_click_x-self.offset_X, self.segundo_click_x-self.offset_X]) / self.factor_escala_dimension_x),
                                                          int(min([self.primer_click_y-self.offset_Y, self.segundo_click_y-self.offset_Y]
                                                                  ) / self.factor_escala_dimension_y),
                                                          int(max([self.primer_click_x-self.offset_X, self.segundo_click_x-self.offset_X]
                                                                  ) / self.factor_escala_dimension_x),
                                                          int(max([self.primer_click_y-self.offset_Y, self.segundo_click_y-self.offset_Y])/self.factor_escala_dimension_y)]

                            # Se va actualizando un diccionario que contiene las clases de los defectos y las coordenadas de cada una de las regiones

                            self.DICC_COORDENADAS_PRODUCTOS_AUX = almacena_coordenadas_y_producto(
                                self.COORDENADAS_PRODUCTOS, self.id_tipo_producto_error, self.DICC_COORDENADAS_PRODUCTOS_AUX, flag_nueva_imagen=self.NUEVA_IMAGEN)

                        # Se activa el boton de borrar por si se quiere borrar la coordenada introducida
                        self.boton_borrar.setEnabled(True)
                        self.boton_validar.setEnabled(True)
                        self.boton_cancelar.setEnabled(True)
                        self.NUEVA_IMAGEN = False

                    else:
                        self.FLAG_PRIMER_CLICK = False
                        self.FLAG_SEGUNDO_CLICK = True
                except:
                    crea_mensaje_alerta(
                        "Si vas a dibujar sobre la imagen, primero selecciona un tipo de defecto.")

        elif self.FLAG_BORRAR:

            self.click_borrar = self.visor.mapFromParent(event.pos())
            self.click_borrar_x = self.click_borrar.x()+self.dim_horizontal_spacer
            self.click_borrar_y = self.click_borrar.y()

            if comprueba_click_dentro_imagen(self.click_borrar_x, self.click_borrar_x, self.ancho_zonaClick_imagen, self.alto_zonaClick_imagen):

                # self.FLAG_PRIMER_CLICK = True
                # self.FLAG_SEGUNDO_CLICK = False

                coordenadas_click = [
                    (self.click_borrar_x), (self.click_borrar_y)]

                self.DICC_COORDENADAS_DEFECTOS_AUX, click_correcto1 = borrar_region(coordenadas_click, self.DICC_COORDENADAS_DEFECTOS_AUX, self.offset_X,
                                                                                    self.offset_Y, self.factor_escala_dimension_x, self.factor_escala_dimension_y)
                self.DICC_COORDENADAS_PRODUCTOS_AUX, click_correcto2 = borrar_region(coordenadas_click, self.DICC_COORDENADAS_PRODUCTOS_AUX, self.offset_X,
                                                                                     self.offset_Y, self.factor_escala_dimension_x, self.factor_escala_dimension_y)

                if click_correcto1 or click_correcto2:
                    self.coloca_imagen_en_visor(
                        self.imagen_capturada, self.imagen_capturada2, self.FLAG_BORRAR)

                    for keys, values in self.DICC_COORDENADAS_DEFECTOS_AUX.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y

                                dibuja_region(QPainter(self.visor.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                    for keys, values in self.DICC_COORDENADAS_DEFECTOS_AUX2.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y2
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y2

                                dibuja_region(QPainter(self.visor_2.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                        else:
                            continue

                    for keys, values in self.DICC_COORDENADAS_PRODUCTOS_AUX.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y

                                dibuja_region(QPainter(self.visor.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                    for keys, values in self.DICC_COORDENADAS_PRODUCTOS_AUX2.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y2
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y2

                                dibuja_region(QPainter(self.visor_2.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

    def mousePressEvent2(self, event):
        """Depende del flag activado, se dibuja o se borra. Se comprueba si el click se ha realizado dentro de la imagen,
        se ve el tipo de defecto seleccionado, y se dibuja de su respectivo color teniendo en cuenta los factores de
        escala.En el caso de borrar, se comrprueba que el click se ha realizado dentro de la region, se elimina esta,
        y se vuelve a dibujar el resto automaticamente"""

        if self.FLAG_DIBUJAR:

            if self.FLAG_PRIMER_CLICK:
                self.primer_click = self.visor_2.mapFromParent(event.pos())
                self.primer_click_x = self.primer_click.x(
                ) + (self.ancho_zonaClick_imagen2[1]) + self.dim_horizontal_spacer
                self.primer_click_y = self.primer_click.y()

                if comprueba_click_dentro_imagen(self.primer_click_x, self.primer_click_y, self.ancho_zonaClick_imagen2, self.alto_zonaClick_imagen2):

                    self.FLAG_PRIMER_CLICK = False
                    self.FLAG_SEGUNDO_CLICK = True

                else:
                    self.FLAG_PRIMER_CLICK = True
                    self.FLAG_SEGUNDO_CLICK = False

            elif self.FLAG_SEGUNDO_CLICK:
                try:
                    color = COLORES_DEFECTOS[self.id_tipo_defecto]

                    self.segundo_click = self.visor_2.mapFromParent(
                        event.pos())
                    self.segundo_click_x = self.segundo_click.x(
                    ) + (self.ancho_zonaClick_imagen2[1]) + self.dim_horizontal_spacer
                    self.segundo_click_y = self.segundo_click.y()

                    if comprueba_click_dentro_imagen(self.segundo_click_x, self.segundo_click_y, self.ancho_zonaClick_imagen2, self.alto_zonaClick_imagen2):

                        self.FLAG_PRIMER_CLICK = True
                        self.FLAG_SEGUNDO_CLICK = False

                        dibuja_region(QPainter(self.visor_2.pixmap()), self.primer_click_x, self.primer_click_y,
                                      self.segundo_click_x, self.segundo_click_y, color, 3, self.offset_X2, self.offset_Y2)

                        self.update()
                        self.visor_2.update()

                        if self.DEFECTO_CLICK:

                            self.COORDENADAS2_DEFECTOS = [int(min([self.primer_click_x-self.offset_X2, self.segundo_click_x-self.offset_X2]) / self.factor_escala_dimension_x2),
                                                          int(min([self.primer_click_y-self.offset_Y2, self.segundo_click_y-self.offset_Y2]
                                                                  ) / self.factor_escala_dimension_y2),
                                                          int(max([self.primer_click_x-self.offset_X2, self.segundo_click_x-self.offset_X2]
                                                                  ) / self.factor_escala_dimension_x2),
                                                          int(max([self.primer_click_y-self.offset_Y2, self.segundo_click_y-self.offset_Y2])/self.factor_escala_dimension_y2)]

                            # Se va actualizando un diccionario que contiene las clases de los defectos y las coordenadas de cada una de las regiones

                            self.DICC_COORDENADAS_DEFECTOS_AUX2 = almacena_coordenadas_y_defecto(
                                self.COORDENADAS2_DEFECTOS, self.id_tipo_defecto, self.DICC_COORDENADAS_DEFECTOS_AUX2, flag_nueva_imagen=self.NUEVA_IMAGEN)

                        else:

                            self.COORDENADAS2_PRODUCTOS = [int(min([self.primer_click_x-self.offset_X2, self.segundo_click_x-self.offset_X2]) / self.factor_escala_dimension_x2),
                                                           int(min([self.primer_click_y-self.offset_Y2, self.segundo_click_y-self.offset_Y2]
                                                                   ) / self.factor_escala_dimension_y2),
                                                           int(max([self.primer_click_x-self.offset_X2, self.segundo_click_x-self.offset_X2]
                                                                   ) / self.factor_escala_dimension_x2),
                                                           int(max([self.primer_click_y-self.offset_Y2, self.segundo_click_y-self.offset_Y2])/self.factor_escala_dimension_y2)]

                            # Se va actualizando un diccionario que contiene las clases de los defectos y las coordenadas de cada una de las regiones

                            self.DICC_COORDENADAS_PRODUCTOS_AUX2 = almacena_coordenadas_y_producto(
                                self.COORDENADAS2_PRODUCTOS, self.id_tipo_producto_error, self.DICC_COORDENADAS_PRODUCTOS_AUX2, flag_nueva_imagen=self.NUEVA_IMAGEN)

                        # Se activa el boton de borrar por si se quiere borrar la coordenada introducida
                        self.boton_borrar.setEnabled(True)
                        self.boton_validar.setEnabled(True)
                        self.boton_cancelar.setEnabled(True)
                        self.NUEVA_IMAGEN = False

                    else:
                        self.FLAG_PRIMER_CLICK = False
                        self.FLAG_SEGUNDO_CLICK = True
                except:
                    crea_mensaje_alerta(
                        "Si vas a dibujar sobre la imagen, primero selecciona un tipo de defecto.")

        elif self.FLAG_BORRAR:

            self.click_borrar = self.visor_2.mapFromParent(event.pos())
            self.click_borrar_x = self.click_borrar.x(
            ) + (self.ancho_zonaClick_imagen2[1]) + self.dim_horizontal_spacer
            self.click_borrar_y = self.click_borrar.y()

            if comprueba_click_dentro_imagen(self.click_borrar_x, self.click_borrar_x, self.ancho_zonaClick_imagen2, self.alto_zonaClick_imagen2):

                # self.FLAG_PRIMER_CLICK = True
                # self.FLAG_SEGUNDO_CLICK = False

                coordenadas_click = [
                    (self.click_borrar_x), (self.click_borrar_y)]

                self.DICC_COORDENADAS_DEFECTOS_AUX2, click_correcto1 = borrar_region(coordenadas_click, self.DICC_COORDENADAS_DEFECTOS_AUX2, self.offset_X2,
                                                                                     self.offset_Y2, self.factor_escala_dimension_x2, self.factor_escala_dimension_y2)
                self.DICC_COORDENADAS_PRODUCTOS_AUX2, click_correcto2 = borrar_region(coordenadas_click, self.DICC_COORDENADAS_PRODUCTOS_AUX2, self.offset_X2,
                                                                                      self.offset_Y2, self.factor_escala_dimension_x2, self.factor_escala_dimension_y2)

                if click_correcto1 or click_correcto2:
                    self.coloca_imagen_en_visor(
                        self.imagen_capturada, self.imagen_capturada2, self.FLAG_BORRAR)

                    for keys, values in self.DICC_COORDENADAS_DEFECTOS_AUX2.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y2
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x2
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y2

                                dibuja_region(QPainter(self.visor_2.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                    for keys, values in self.DICC_COORDENADAS_DEFECTOS_AUX.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y

                                dibuja_region(QPainter(self.visor.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                        else:
                            continue

                    for keys, values in self.DICC_COORDENADAS_PRODUCTOS_AUX.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y

                                dibuja_region(QPainter(self.visor.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)

                        else:
                            continue

                    for keys, values in self.DICC_COORDENADAS_PRODUCTOS_AUX2.items():
                        if values[1] != '-':
                            try:
                                color = COLORES_DEFECTOS[keys]

                            except:
                                color = 'black'

                            for coordenadas in values[1]:

                                coordenada_x_min = coordenadas[0] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_min = coordenadas[1] * \
                                    self.factor_escala_dimension_y
                                coordenada_x_max = coordenadas[2] * \
                                    self.factor_escala_dimension_x
                                coordenada_y_max = coordenadas[3] * \
                                    self.factor_escala_dimension_y

                                dibuja_region(QPainter(self.visor_2.pixmap()), coordenada_x_min, coordenada_y_min,
                                              coordenada_x_max, coordenada_y_max, color, 3, 0, 0)


# ================================================== CONFIRMAR / CANCELAR DEFECTOS =====================================

    def fn_boton_validar(self):
        """Se utiliza el diccioanrio de coordenadas y defectos para crear un fichero xml y dos imagenes, una pintada, y otra sin pintar"
        """
        try:
            nombre_cliente_comboBox = self.comboBox_ampolla.currentText()
            nombre_cliente = DICCIONARIO_COORDENADAS_PRODUCTO[nombre_cliente_comboBox][2]

            self.DICC_COORDENADAS_PRODUCTOS_AUX[nombre_cliente_comboBox][1] = [
                [0, 0, self.imagen_capturada.width(),  self.imagen_capturada.height()]]
            self.DICC_COORDENADAS_PRODUCTOS_AUX2[nombre_cliente_comboBox][1] = [
                [0, 0, self.imagen_capturada2.width(),  self.imagen_capturada2.height()]]

            guarda_imagen_y_anotacion(imagen_pintada=self.visor.pixmap(
            ), imagen_original=self.imagen_capturada, DICC_COORDENADAS_DEFECTOS_AUX=self.DICC_COORDENADAS_DEFECTOS_AUX, DICC_COORDENADAS_PRODUCTOS_AUX=self.DICC_COORDENADAS_PRODUCTOS_AUX, imagen_pintada2=self.visor_2.pixmap(
            ), imagen_original2=self.imagen_capturada2, DICC_COORDENADAS_DEFECTOS_AUX2=self.DICC_COORDENADAS_DEFECTOS_AUX2, DICC_COORDENADAS_PRODUCTOS_AUX2=self.DICC_COORDENADAS_PRODUCTOS_AUX2, nombre_cliente=nombre_cliente)

            self.visor.clear()
            self.visor_2.clear()
            elimina_imagen_temporal()
            self.detecta_imagen()

            self.COORDENADAS_DEFECTOS = []
            self.COORDENADAS2_DEFECTOS = []
            self.COORDENADAS_PRODUCTOS = []
            self.COORDENADAS2_PRODUCTOS = []
            self.FLAG_CAPTURA_IMAGEN = False
            self.NUEVA_IMAGEN = True
            self.comboBox_ampolla_error.setCurrentIndex(0)

        except:
            crea_mensaje_alerta("Selecciona antes el tipo de ampolla")
            self.boton_cancelar.setEnabled(True)
            self.boton_validar.setEnabled(True)

    def fn_boton_cancelar(self):
        "Al pulsar este boton, se cancela todo lo dibujado y se vuelve a ejecutar el video."

        self.coloca_imagen_en_visor(
            self.imagen_capturada, self.imagen_capturada2, 1)
        self.FLAG_CAPTURA_IMAGEN = False
        self.NUEVA_IMAGEN = True
        self.COORDENADAS_DEFECTOS = []
        self.COORDENADAS2_DEFECTOS = []
        self.DICC_COORDENADAS_DEFECTOS_AUX = copy.deepcopy(
            DICCIONARIO_COORDENADAS_DEFECTOS)
        self.DICC_COORDENADAS_DEFECTOS_AUX2 = copy.deepcopy(
            DICCIONARIO_COORDENADAS_DEFECTOS)
        self.COORDENADAS_PRODUCTOS = []
        self.COORDENADAS2_PRODUCTOS = []
        self.DICC_COORDENADAS_PRODUCTOS_AUX = copy.deepcopy(
            DICCIONARIO_COORDENADAS_PRODUCTO)
        self.DICC_COORDENADAS_PRODUCTOS_AUX2 = copy.deepcopy(
            DICCIONARIO_COORDENADAS_PRODUCTO)
        self.comboBox_ampolla_error.setCurrentIndex(0)

 # ============================================== FUNCIONES CERRAR VENTANA ============================================
        """A traves de estas funciones se define la logica de cierre de ventana.
        """

    def closeEvent(self, event):
        """
        Cerrar la ventana a través de el boton X de la esquina supeior derecha

        :param event: evento del raton
        :return: None
        """
        close = QMessageBox.question(self,
                                     "SALIR",
                                     "¿ESTAS SEGURO/A DE QUERER SALIR?",
                                     QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            event.accept()
            sys.exit()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        """
        Cerrar la ventana a traves de la tecla ESC

        :param e: evento del teclado
        :return: None
        """
        if e.key() == QtCore.Qt.Key_Escape:
            self.closeEvent(e)
            self.close()
        if e.key() == QtCore.Qt.Key_F11:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

 # ================================================== INICIA APLICACION ================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = Main()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
    # app.exec()
