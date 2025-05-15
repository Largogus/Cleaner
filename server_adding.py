from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from CustomListWidget import CustomListWidget
import sys
import os
import json
import create_properties
from loguru import logger


class ServerAdding(QDialog):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('Добавить компьютер')

        self.layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setText('Добавить компьютер')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 15))

        self.line_name = QLineEdit()
        self.line_name.setPlaceholderText('Добавить название компьютера')
        self.line_name.setFont(QFont('Arial', 15))

        self.line_ip = QLineEdit()
        self.line_ip.setPlaceholderText('Добавить IP компьютера')
        self.line_ip.setFont(QFont('Arial', 15))

        self.save = QPushButton()
        self.save.setText('Сохранить')
        self.save.setFont(QFont('Arial', 15))
        self.save.clicked.connect(self.saveFunc)

        self.layout.addSpacing(10)
        self.layout.addWidget(self.label)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.line_name)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.line_ip)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.save)
        self.layout.addSpacing(10)

        self.setLayout(self.layout)

    def saveFunc(self):
        with open('properties.json', 'r', encoding='utf-8') as f:
            lst = json.load(f)

        if self.line_ip.text() == "" or self.line_name.text() == "":
            QMessageBox.warning(self, "Ошибка", 'Не должно остаться пустых строк')
            return

        for i in lst['connected-ip']:
            if self.line_name.text() in i:
                QMessageBox.warning(self, "Ошибка", 'Такой название уже есть')
                return

            if self.line_ip.text() in i:
                QMessageBox.warning(self, "Ошибка", 'Такой ip уже есть')
                return

        lst['connected-ip'].append([self.line_name.text(), self.line_ip.text()])

        with open('properties.json', 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=4)

        self.close()