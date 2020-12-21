from PyQt5.QtWidgets import QMessageBox


def crea_mensaje_alerta(texto):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(texto)
    msg.setWindowTitle("Aviso")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
