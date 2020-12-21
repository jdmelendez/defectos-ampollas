from GUI_config import DICCIONARIO_COORDENADAS_PRODUCTO
import copy


def almacena_coordenadas_y_producto(coordenadas, tipo_defecto, diccionario_coord_prod, flag_nueva_imagen, dicc=DICCIONARIO_COORDENADAS_PRODUCTO):

    if flag_nueva_imagen:
        dict_ = copy.deepcopy(dicc)
        diccionario_coord_prod = dict_

    if diccionario_coord_prod[tipo_defecto][1] == '-':
        diccionario_coord_prod[tipo_defecto][1] = [coordenadas]
    else:
        diccionario_coord_prod[tipo_defecto][1].append(coordenadas)

    return diccionario_coord_prod
