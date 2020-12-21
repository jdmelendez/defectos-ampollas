from dict2xml import dict2xml


def crea_xml(DICC_COORDENADAS_DEFECTOS_AUX, label):

    clases = []
    coordenadas = []

    for valores in DICC_COORDENADAS_DEFECTOS_AUX.values():
        clases.append(valores[0])
        coordenadas_str = ''

        # Creamos un string con las coordenadas de manera que su pueda escribir en el fichero xml
        if valores[1] != '-':
            for i in valores[1]:
                for indice, j in enumerate(i):
                    if indice != 3:
                        coordenadas_str = coordenadas_str + str(j) + ','
                    else:
                        coordenadas_str = coordenadas_str + str(j)

                coordenadas_str = coordenadas_str + '; '
        else:
            coordenadas_str = valores[1]

        coordenadas.append(coordenadas_str)

    diccionario = dict(zip(clases, coordenadas))

    xml = dict2xml(diccionario, wrap=label)  # , indent ="   ")

    return xml
