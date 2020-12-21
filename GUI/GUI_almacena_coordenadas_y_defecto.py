from GUI_config import DICCIONARIO_COORDENADAS_DEFECTOS
import copy


def almacena_coordenadas_y_defecto(coordenadas, tipo_producto_error, diccionario_coord_def, flag_nueva_imagen, dicc=DICCIONARIO_COORDENADAS_DEFECTOS):

    if flag_nueva_imagen:
        dict_ = copy.deepcopy(dicc)
        diccionario_coord_def = dict_

    if diccionario_coord_def[tipo_producto_error][1] == '-':
        diccionario_coord_def[tipo_producto_error][1] = [coordenadas]
    else:
        diccionario_coord_def[tipo_producto_error][1].append(coordenadas)

    return diccionario_coord_def
