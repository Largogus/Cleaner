import json
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtNetwork import QTcpSocket
from loguru import logger


class ServerEdit(QDialog):
    def __init__(self, data, main_app):
        super().__init__()

        self.main_app = main_app
        self.data = data

        with open('properties.json', 'r', encoding='utf-8') as f:
            self.lst = json.load(f)

        for i in self.lst['connected-ip']:
            if self.data in i:
                self.name = i[0]
                self.ip = i[1]
                self.index = self.lst['connected-ip'].index(i)

        self.setGeometry(300, 300, 500, 200)
        self.setWindowTitle('Управление компьютером')

        self.layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setText('Управление компьютером')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 15))

        self.frame1 = QFrame()
        frame1 = QVBoxLayout()

        self.line_name = QLineEdit()
        self.line_name.setText(self.name)
        self.line_name.setFont(QFont('Arial', 15))

        self.line_ip = QLineEdit()
        self.line_ip.setText(self.ip)
        self.line_ip.setFont(QFont('Arial', 15))

        self.save = QPushButton()
        self.save.setText('Сохранить изменения')
        self.save.setFont(QFont('Arial', 15))
        self.save.clicked.connect(self.edit)

        self.internet = QPushButton()
        self.internet.setFont(QFont('Arial', 15))
        self.internet.clicked.connect(self.toggle_internet)
        self.internet.setText("Удалить Roblox")

        frame1.addSpacing(10)
        frame1.addWidget(self.line_name)
        frame1.addSpacing(20)
        frame1.addWidget(self.line_ip)
        frame1.addSpacing(20)
        frame1.addWidget(self.save)
        frame1.addSpacing(10)
        frame1.addWidget(self.internet)
        frame1.addSpacing(10)

        self.layout.addWidget(self.label)
        self.frame1.setLayout(frame1)
        self.layout.addWidget(self.frame1)

        self.setLayout(self.layout)

    def edit(self):
        with open('properties.json', 'r', encoding='utf-8') as f:
            lst = json.load(f)

        lst['connected-ip'][self.index] = [self.line_name.text(), self.line_ip.text()]

        with open('properties.json', 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=4)

        self.main_app.update_allowed_ips()
        self.main_app.list_ip.update_table()

    def toggle_internet(self):
        self.main_app.changeInternetForOne(self.name, self.ip, self.index)