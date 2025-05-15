from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QDialog, QVBoxLayout, QFrame, QLineEdit,
                             QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QFont
import sys
import os
import json
from socket import gethostname, gethostbyname
import bcrypt


class CreateProperties(QDialog):
    def __init__(self, types: str, data=None):
        super().__init__()

        self.data = data
        self.type = types
        self.setGeometry(600, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowTitle('Настройте property.json')

        self.main_lay = QVBoxLayout()

        self.labl_lay = QVBoxLayout()
        self.labl_lay.setAlignment(Qt.AlignCenter)

        self.lab = QLabel()
        self.lab.setFont(QFont('Arial', 15))
        self.lab.setText('Настройте property.json')
        self.labl_lay.addWidget(self.lab)

        self.tab1 = QFrame()

        tab_input_1 = QVBoxLayout()

        self.host_ip_label = QLabel()
        self.host_ip_label.setText('Введите ip-адрес компьютора хоста:')
        self.host_ip_label.setFont((QFont('Arial', 15)))

        hostname = gethostname()
        ip_address = gethostbyname(hostname)

        self.host_ip = QLineEdit()
        self.host_ip.setText(ip_address)
        self.host_ip.setFont((QFont('Arial', 15)))

        tab_input_1.addWidget(self.host_ip_label)
        tab_input_1.addWidget(self.host_ip)

        self.tab1.setLayout(tab_input_1)

        self.tab2 = QFrame()

        tab_input_2 = QVBoxLayout()

        self.host_password_label = QLabel()
        self.host_password_label.setText('Введите пароль админа:')
        self.host_password_label.setFont((QFont('Arial', 15)))

        self.host_password = QLineEdit()
        self.host_password.setFont((QFont('Arial', 15)))

        tab_input_2.addWidget(self.host_password_label)
        tab_input_2.addWidget(self.host_password)

        self.tab2.setLayout(tab_input_2)

        self.save = QPushButton()
        self.save.setText('Сохранить')
        self.save.setFont((QFont('Arial', 15)))
        self.save.clicked.connect(self.saveFunc)

        self.main_lay.addLayout(self.labl_lay)
        self.main_lay.addWidget(self.tab1)
        self.main_lay.addSpacing(10)
        self.main_lay.addWidget(self.tab2)
        self.main_lay.addSpacing(30)
        self.main_lay.addWidget(self.save)
        self.main_lay.addSpacing(20)
        self.setLayout(self.main_lay)

    def saveFunc(self):
        password = self.host_password.text().encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        stored_hash = hashed.decode('utf-8')

        # path = os.getcwd()
        # properties = os.path.join(path, "properties.json")
        #
        # if not properties:

        if self.type == 'locked':
            with open('properties.json', 'r', encoding='utf-8') as f:
                texts = json.load(f)

            text, ok = QInputDialog().getText(self, "Введите пароль)",
                                              "Пароль админа:", QLineEdit.Normal,
                                              QDir().home().dirName())

            if not bcrypt.checkpw(text.encode('utf-8'), texts["owner-password"].encode('utf-8')):
                QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
                return

            texts['owner-password'] = stored_hash

        if self.type == 'open':
            with open('properties.json', 'w', encoding='utf-8') as f:
                lst = {
                    'owner-ip': self.host_ip.text(),
                    'owner-password': stored_hash,
                    'connected-ip': []
                }

        json.dump(lst, f, ensure_ascii=False, indent=4)

        self.close()

        if self.data is not None:
            self.data_class = self.data()
            self.data_class.show()


class CreateLocal(QDialog):
    def __init__(self, type, data=None):
        super().__init__()

        self.type = type
        self.data = data
        self.setGeometry(600, 300, 600, 400)
        self.setMinimumSize(600, 400)
        self.setWindowTitle('Настройте local.json')

        self.main_lay = QVBoxLayout()

        self.labl_lay = QVBoxLayout()
        self.labl_lay.setAlignment(Qt.AlignCenter)

        self.lab = QLabel()
        self.lab.setFont(QFont('Arial', 15))
        self.lab.setText('Настройте local.json')
        self.labl_lay.addWidget(self.lab)

        self.tab1 = QFrame()

        tab_input_1 = QVBoxLayout()

        self.host_ip_label = QLabel()
        self.host_ip_label.setText('Введите ip-адрес сервера:')
        self.host_ip_label.setFont((QFont('Arial', 15)))

        self.host_ip = QLineEdit()
        self.host_ip.setFont((QFont('Arial', 15)))

        tab_input_1.addWidget(self.host_ip_label)
        tab_input_1.addWidget(self.host_ip)

        self.tab1.setLayout(tab_input_1)

        self.save = QPushButton()
        self.save.setText('Сохранить')
        self.save.setFont((QFont('Arial', 15)))
        self.save.clicked.connect(self.saveFunc)

        self.main_lay.addLayout(self.labl_lay)
        self.main_lay.addWidget(self.tab1)
        self.main_lay.addSpacing(30)
        self.main_lay.addWidget(self.save)
        self.main_lay.addSpacing(20)
        self.setLayout(self.main_lay)

    def saveFunc(self):
        with open('properties.json', 'r', encoding='utf-8') as f:
            lst = json.load(f)

        if self.type == 'locked':
            text, ok = QInputDialog().getText(self, "Введите пароль",
                                              "IP компьюетра:", QLineEdit.Normal)

            if ok:
                if bcrypt.checkpw(text.encode('utf-8'), lst['owner-password'].encode('utf-8')):
                    lst[''] = self.host_ip.text()
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
                    return

                with open('local.json', 'w', encoding='utf-8') as f:
                    lst = {
                        'ip': self.host_ip.text(),
                        'port': 12345
                    }

                    json.dump(lst, f, ensure_ascii=False, indent=4)
        else:
            with open('local.json', 'w', encoding='utf-8') as f:
                lst = {
                    'ip': self.host_ip.text(),
                    'port': 12345
                }

                json.dump(lst, f, ensure_ascii=False, indent=4)

        self.close()

        if self.data is not None:
            self.data_class = self.data()
            self.data_class.show()