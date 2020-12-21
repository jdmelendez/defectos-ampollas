from PyQt5.QtGui import QColor, QImage, QPixmap, QPen, QPainter, QFont


def borrar_region(coordenadas_click, diccionario_coordenadas_defectos, offset_X=0, offset_Y=0, factor_escala_x=0, factor_escala_y=0):

    box_a_borrar, click_correcto = obten_region_a_borrar(
        coordenadas_click, diccionario_coordenadas_defectos, factor_escala_x, factor_escala_y, offset_X, offset_Y)

    # diccionario = {}

    if click_correcto:
        diccionario = actualiza_diccionario(
            diccionario_coordenadas_defectos, box_a_borrar)
    else:
        diccionario = diccionario_coordenadas_defectos

    #     painter.drawRect((box_a_borrar[0]*factor_escala_x), (box_a_borrar[1]*factor_escala_y),
    #                      (box_a_borrar[2]-box_a_borrar[0])*factor_escala_x, (box_a_borrar[3]-box_a_borrar[1])*factor_escala_y)

    return diccionario, click_correcto


def obten_region_a_borrar(coordenadas_click, diccionario_coordenadas_defectos, factor_escala_x, factor_escala_y, offset_X, offset_Y):

    x = (coordenadas_click[0]-offset_X) / factor_escala_x
    y = (coordenadas_click[1] - offset_Y) / factor_escala_y

    lista_propuesta_regiones_a_borrar = []
    lista_areas_propuestas_regiones_a_borrar = []

    for valores in diccionario_coordenadas_defectos.values():
        boxes_existentes = valores[1]

        if boxes_existentes == '-':
            continue

        # Obtenemos las regiones cuyo click esta contenido en su interior
        for box in boxes_existentes:
            xmax_box = int(box[2])
            ymax_box = int(box[3])
            xmin_box = int(box[0])
            ymin_box = int(box[1])

            if x > xmin_box and y > ymin_box and x < xmax_box and y < ymax_box:
                propuesta_region_a_borar = [
                    xmin_box, ymin_box, xmax_box, ymax_box]
                lista_areas_propuestas_regiones_a_borrar.append(
                    calcula_area_region(xmin_box, ymin_box, xmax_box, ymax_box))
                lista_propuesta_regiones_a_borrar.append(
                    propuesta_region_a_borar)

    # En caso de clicar en una zona de union entre dos regiones, decidimos por la de area mas pequeña
    if len(lista_propuesta_regiones_a_borrar) > 1:
        indice_area_menor = lista_areas_propuestas_regiones_a_borrar.index(
            min(lista_areas_propuestas_regiones_a_borrar))
        region_a_borrar = lista_propuesta_regiones_a_borrar[indice_area_menor]
        click_correcto = True

    elif len(lista_propuesta_regiones_a_borrar) == 1:
        region_a_borrar = lista_propuesta_regiones_a_borrar[0]
        click_correcto = True
    else:
        region_a_borrar = []
        click_correcto = False

    return region_a_borrar, click_correcto


def calcula_area_region(xmin, ymin, xmax, ymax):
    area = (xmax - xmin) * (ymax - ymin)
    return area


def actualiza_diccionario(diccionario, box_a_borrar):

    clases = []
    valores = []

    for key, values in diccionario.items():

        clases.append(key)

        coordenadas = []

        if values[1] != '-':
            for coordenada in values[1]:
                if coordenada == box_a_borrar:
                    continue

                coordenadas.append(coordenada)
        else:
            coordenadas = values[1]

        if coordenadas == []:
            coordenadas = '-'

        valores_aux = [values[0], coordenadas, values[2]]

        valores.append(valores_aux)

    diccionario = dict(zip(clases, valores))

    return diccionario
