from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QStandardItemModel
from GUI_config import PATH_IMGS_PRUEBA


def lista_resto_directorios(Qlist_origen, Qlist_destino, Qlist_a_vaciar, dirModel, limpia_lista=0):

    if limpia_lista:
        model = QStandardItemModel()
        Qlist_a_vaciar.setModel(model)
        model.removeRow(0)

    index = Qlist_origen.currentIndex()
    path_seleccionado_del_directorio = dirModel.filePath(index)

#   dirModel.setNameFilters(["*A.png", "*C.png*", "*B.png", "*S.png", "*E.png", "*R.png", "*0.png", "*1.png",
#                              "*2.png", "*3.png", "*4.pn  g", "*5.png", "*6.png", "*7.png", "*8.png", "*9.png"])
#     # dirModel.setNameFilters(["*C.png", "*1.png"])
#     dirModel.setNameFilterDisables(0)

    Qlist_destino.setModel(dirModel)
    Qlist_destino.setRootIndex(dirModel.index(
        path_seleccionado_del_directorio))


def lista_primer_directorio(Qlist, dirModel, path=PATH_IMGS_PRUEBA):

    Qlist.setModel(dirModel)
    Qlist.setRootIndex(dirModel.index(path))
