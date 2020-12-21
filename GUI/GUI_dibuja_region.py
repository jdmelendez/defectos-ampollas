from PyQt5.QtGui import QColor, QImage, QPixmap, QPen, QPainter, QFont, QStandardItemModel


def dibuja_region(painter, primer_punto_x, primer_punto_y, segundo_punto_x, segundo_punto_y, color, px, offset_X=0, offset_Y=0):

    pen = QPen()
    pen.setColor(QColor(color))
    pen.setWidth(px)
    painter.setPen(pen)
    painter.drawRect(primer_punto_x-offset_X, primer_punto_y-offset_Y,
                     segundo_punto_x-primer_punto_x, segundo_punto_y-primer_punto_y)
