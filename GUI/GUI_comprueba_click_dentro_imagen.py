def comprueba_click_dentro_imagen(coordendas_click_x, coordendas_click_y, ancho_zona_click, alto_zona_click):
    """Con esta funcion se comprueba si el click realizado en el modo edicion se encuentra dentro de los limites de la imagen.
    Para ello, se recibe la coordenada x,y del click, y la coordenada minima y maxima tanto del alto como el ancho de la
    imagen.

    Returns: Se devuelve una variable booleana que dice si el click se ha efectuado dentro de la imagen o no.

    """
    if (coordendas_click_x > ancho_zona_click[0] and coordendas_click_x < ancho_zona_click[1]) and (coordendas_click_y > alto_zona_click[0] and coordendas_click_y < alto_zona_click[1]):
        click_dentro = True

    else:
        click_dentro = False

    return click_dentro
