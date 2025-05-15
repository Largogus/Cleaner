from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, QFrame, QInputDialog,
                             QLineEdit, QAction, QMenu, QSystemTrayIcon)
from PyQt5.QtCore import QSize, QTimer, QByteArray
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from CustomListWidget import CustomListWidget
import sys
import os
import json
import create_properties
from loguru import logger
from server_adding import ServerAdding


path = os.getcwd()


class App(QWidget):
    def __init__(self):
        super().__init__()
        logger.add("log\\logs_{time:YYYY-MM-DD}.log", rotation='00:00', retention='1 day',
                   compression='zip')

        self.tcp_server = QTcpServer(self)
        self.tcp_server.newConnection.connect(self.new_client_connection)
        self.clients = []
        self.client_address = []
        self.allowed_ips = self.load_allowed_ips()

        properties = os.path.join(path, "properties.json")
        with open(properties, 'r', encoding='utf-8') as f:
            self.lst = json.load(f)

        self.setGeometry(600, 100, 1000, 730)
        self.setWindowTitle('Очиститель (Сервер)')
        self.setWindowIcon(QIcon('img/clear.png'))

        self.main_layout = QVBoxLayout()

        self.edit_properties = QPushButton()
        self.edit_properties.setText('Изменить properties.json')
        self.edit_properties.setFont(QFont('Arial', 15))
        self.edit_properties.clicked.connect(self.editProperties)

        self.turn_internet = QPushButton()
        self.turn_internet.setText("Удалить Roblox")
        self.turn_internet.setFont(QFont('Arial', 15))
        self.turn_internet.clicked.connect(self.send_now)

        self.main_tab = QFrame()
        tabh = QHBoxLayout()

        self.tab1 = QFrame()
        tab1 = QVBoxLayout()

        self.list_ip = CustomListWidget('connected-ip', self.client_address, self.parent())

        tab_1h = QHBoxLayout()

        self.button_write_wb = QPushButton()
        self.button_write_wb.setIcon(QIcon('img/pen.png'))
        self.button_write_wb.setIconSize(QSize(30, 30))
        self.button_write_wb.clicked.connect(self.createPC)
        self.button_write_wb.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                border: 1px solid black;
            }
            
            QPushButton:pressed {
                background-color: rgba(196, 196, 196, 0.5);
            }
        ''')

        self.button_delete_wb = QPushButton()
        self.button_delete_wb.setIcon(QIcon('img/trash.png'))
        self.button_delete_wb.setIconSize(QSize(30, 30))
        self.button_delete_wb.clicked.connect(self.delete_pc)
        self.button_delete_wb.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                border: 1px solid black;
            }
            QPushButton:pressed {
                background-color: rgba(196, 196, 196, 0.5);
            }
        ''')

        tab_1h.addWidget(self.button_write_wb)
        tab_1h.addWidget(self.button_delete_wb)

        tab1.addWidget(self.list_ip)
        tab1.addLayout(tab_1h)

        self.tab1.setLayout(tab1)

        tabh.addWidget(self.tab1)

        self.main_tab.setLayout(tabh)

        self.main_layout.addWidget(self.edit_properties)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.turn_internet)
        self.main_layout.addWidget(self.main_tab)
        self.setLayout(self.main_layout)

        self.update_allowed_timer = QTimer(self)
        self.update_allowed_timer.timeout.connect(self.update_allowed_ips)
        self.update_allowed_timer.start(10 * 60 * 100)

        self.broadcast_timer = QTimer(self)
        self.broadcast_timer.timeout.connect(self.list_ip.update_table)
        self.broadcast_timer.start(10 * 60)

        if not self.tcp_server.listen(QHostAddress.Any, 12345):
            logger.error(f'Не удалось запустить сервер: {self.tcp_server.errorString()}')
        else:
            logger.success(f'Сервер запущен на порту: {self.tcp_server.serverPort()}')

        self.create_tray()

    def create_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(f'img/clear.png'))
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip('Очиститель (Сервер)')
        self.menu = QMenu()

        self.showAction = QAction('Открыть', self)
        self.showAction.triggered.connect(self.show)

        self.exitAction = QAction('Выйти', self)
        self.exitAction.triggered.connect(self.closer)

        self.menu.addAction(self.showAction)
        self.menu.addAction(self.exitAction)

        self.tray_icon.setContextMenu(self.menu)

        self.tray_icon.activated.connect(self.on_tray)

    def on_tray(self, reason: bool):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def closer(self):
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def load_allowed_ips(self):
        properties = os.path.join(path, "properties.json")

        try:
            with open(properties, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ip[1] for ip in data.get('connected-ip', [])]
        except:
            return []

    def update_allowed_ips(self):
        self.allowed_ips = self.load_allowed_ips()

        for client in self.clients[:]:
            peer_address = client.peerAddress()

            if peer_address.protocol() == QHostAddress.AnyIPv4:
                client_ip = peer_address.toString()
            elif peer_address.protocol() == QHostAddress.AnyIPv6:
                ipv4 = peer_address.toIPv4Address()
                client_ip = QHostAddress(ipv4).toString() if ipv4 != 0 else peer_address.toString()
            else:
                client_ip = peer_address.toString()

            if client_ip.startswith("::ffff:"):
                normalized_ip = client_ip[7:]
            else:
                normalized_ip = client_ip

            if normalized_ip not in self.allowed_ips:
                client.disconnectFromHost()
                self.clients.remove(client)
                logger.info(f"Отключен неавторизованный клиент: {peer_address}")

    def new_client_connection(self):
        client_socket = self.tcp_server.nextPendingConnection()
        peer_address = client_socket.peerAddress()

        if peer_address.protocol() == QHostAddress.AnyIPv4:
            client_ip = peer_address.toString()
        elif peer_address.protocol() == QHostAddress.AnyIPv6:
            ipv4 = peer_address.toIPv4Address()
            client_ip = QHostAddress(ipv4).toString() if ipv4 != 0 else peer_address.toString()
        else:
            client_ip = peer_address.toString()

        if client_ip.startswith("::ffff:"):
            normalized_ip = client_ip[7:]
        else:
            normalized_ip = client_ip

        if normalized_ip in self.allowed_ips:
            self.client_address.append(normalized_ip)
            client_socket.readyRead.connect(lambda: self.read_client_data(client_socket))
            client_socket.disconnected.connect(lambda: self.client_disconnected(client_socket))
            self.clients.append(client_socket)
            logger.success((f"Принято подключение от авторизованного клиента: {normalized_ip}"))
            self.send_to_client(client_socket)
        else:
            logger.info(f"Отклонено подключение от неавторизованного IP: {normalized_ip}")
            client_socket.disconnectFromHost()

    def client_disconnected(self, socket):
        if socket in self.clients:
            self.clients.remove(socket)
            self.client_address.remove(socket.peerAddress().toString().split(':')[-1])
        socket.deleteLater()

    def send_to_client(self, socket):
        try:
            with open('properties.json', 'r', encoding='utf-8') as f:
                lst = json.load(f)

            message = "Start"

            message_js = json.dumps([message, lst['owner-password']]).encode('utf-8')

            byte_array = QByteArray(message_js)

            print(lst['owner-password'])

            bytes_written = socket.write(byte_array)

            if bytes_written == -1:
                logger.error("ОШИБКА")
        except Exception as e:
            logger.error(f"Ошибка отправки данных клиенту: {e}")

    def changeInternetForOne(self, name, ip, index):
        properties = os.path.join(path, "properties.json")
        with open(properties, 'r', encoding='utf-8') as f:
            lst = json.load(f)

        ci = lst['connected-ip']
        ci[index] = [name, ip]

        with open(properties, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=4)

        try:
            for client in self.clients:
                peer_address = client.peerAddress()

                if peer_address.protocol() == QHostAddress.AnyIPv4:
                    client_ip = peer_address.toString()
                elif peer_address.protocol() == QHostAddress.AnyIPv6:
                    ipv4 = peer_address.toIPv4Address()
                    client_ip = QHostAddress(ipv4).toString() if ipv4 != 0 else peer_address.toString()
                else:
                    client_ip = peer_address.toString()

                if client_ip.startswith("::ffff:"):
                    normalized_ip = client_ip[7:]
                else:
                    normalized_ip = client_ip

                if normalized_ip == ip and client.state() == QTcpSocket.ConnectedState:
                    message = "Delete Roblox"

                    message_js = json.dumps([message]).encode('utf-8')

                    byte_array = QByteArray(message_js)

                    bytes_written = client.write(byte_array)

                    if bytes_written == -1:
                        logger.error(f"Ошибка отправки для {normalized_ip}: {client.errorString()}")
                    else:
                        logger.info(f"Данные отправлены {normalized_ip}")
                    break
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")

    def createPC(self):
        serv = ServerAdding()
        serv.exec_()

    def send_now(self):
        try:
            for client in self.clients:
                print(self.clients)
                if client.state() == QTcpSocket.ConnectedState:
                    peer_address = client.peerAddress()

                    normalized_ip = peer_address.toString().split(':')[-1]

                    if normalized_ip in self.allowed_ips:
                        message = "Delete Roblox"

                        message_js = json.dumps([message]).encode('utf-8')

                        byte_array = QByteArray(message_js)

                        bytes_written = client.write(byte_array)
                        if bytes_written == -1:
                            logger.error(f"Ошибка отправки для {normalized_ip}: {client.errorString()}")
                        else:
                            logger.info(f"Данные отправлены {normalized_ip}")
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")

    def editProperties(self):
        apps = create_properties.CreateProperties('locked')
        apps.exec_()

    def delete_pc(self):
        text, ok = QInputDialog().getText(self, "Введите IP",
                                          "IP компьюетра:", QLineEdit.Normal)

        if ok:
            with open('properties.json', 'r', encoding='utf-8') as f:
                lst = json.load(f)

            new_ips = [ip for ip in lst['connected-ip'] if text not in ip]

            if len(new_ips) != len(lst['connected-ip']):
                lst['connected-ip'] = new_ips

            with open('properties.json', 'w', encoding='utf-8') as f:
                json.dump(lst, f, ensure_ascii=False, indent=4)

            logger.success("Элемент удалён")


def check():
    properties = os.path.join(path, "properties.json")

    if not os.path.exists(properties):
        return False

    try:
        with open('properties.json', 'r', encoding='utf-8') as f:
            lst = json.load(f)
    except UnicodeDecodeError:
        with open('properties.json', 'r', encoding='cp1251') as f:
            lst = json.load(f)

    if lst == {}:
        return False

    return True


def start_point():
    app = QApplication(sys.argv)
    wind = App()
    wind.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    if check():
        check()
        app = QApplication(sys.argv)
        wind = App()
        wind.show()
        sys.exit(app.exec_())
    else:
        app = QApplication(sys.argv)
        create = create_properties.CreateProperties('open', App)
        create.show()
        sys.exit(app.exec_())