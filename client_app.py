from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QApplication, QVBoxLayout, QLineEdit,
                             QInputDialog, QMessageBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QDir
from PyQt5.QtGui import QFont, QIcon, QCloseEvent
from PyQt5.QtNetwork import QTcpSocket
import sys
import os
import json
import create_properties
from loguru import logger
import shutil
from win32com.client import Dispatch
import winreg

path = os.getcwd()


class App(QWidget):
    def __init__(self):
        super().__init__()

        logger.add("log/logs_{time:YYYY-MM-DD}.log", rotation='00:00', retention='1 day',
                   compression='zip')
        self.setGeometry(600, 100, 500, 150)
        self.setWindowTitle('Очиститель (Клиент)')
        self.setWindowIcon(QIcon('img/clear.png'))

        self.socket = QTcpSocket(self)
        local = os.path.join(path, "local.json")
        with open(local, 'r') as f:
            lst = json.load(f)

        self.server_ip = lst['ip']
        self.server_port = lst['port']

        self.connect = False

        self.main_layout = QVBoxLayout()

        self.edit_local = QPushButton()
        self.edit_local.setText('Изменить local.json')
        self.edit_local.setFont(QFont('Arial', 15))
        self.edit_local.clicked.connect(self.editLocale)

        tab1 = QVBoxLayout()

        self.label = QLabel()
        self.label.setText('Подключение...')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 20))
        tab1.addWidget(self.label)

        self.main_layout.addWidget(self.edit_local)
        self.main_layout.addLayout(tab1)
        self.setLayout(self.main_layout)

        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setInterval(10000)
        self.reconnect_timer.timeout.connect(self.try_reconnect)

        # self.sync_timer = QTimer(self)
        # self.sync_timer.timeout.connect(self.sync_with_server)
        # self.sync_timer.start(6000)

        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.errorOccurred.connect(self.on_error)
        self.socket.readyRead.connect(self.read_data)

        self.connect_to_server()
        self.create_tray()

    def create_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(f'img/clear.png'))
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip('Очиститель (Клиент)')
        self.menu = QMenu()

        self.showAction = QAction('Открыть', self)
        self.showAction.triggered.connect(self.show)

        self.exitAction = QAction('Выйти', self)
        self.exitAction.triggered.connect(self.verify_password)

        self.menu.addAction(self.showAction)
        self.menu.addAction(self.exitAction)

        self.tray_icon.setContextMenu(self.menu)

        self.tray_icon.activated.connect(self.on_tray)

    def reload_app(self):
        script = sys.executable
        os.execl(script, script, *sys.argv)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def verify_password(self):
        with open('local.json', 'r') as f:
            data = json.load(f)

        if 'owner-password' not in data:
            QApplication.quit()
            return

        text, ok = QInputDialog.getText(
            self,
            "Подтверждение выхода",
            "Введите пароль администратора:",
            QLineEdit.Password
        )

        if ok and text:
            if create_properties.verify_password(data['owner-password'], text):
                QApplication.quit()
            else:
                self.show()
                QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
        else:
            self.show()

    def on_tray(self, reason: bool):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def connect_to_server(self):
        local = os.path.join(path, "local.json")

        with open(local, 'r') as f:
            lst = json.load(f)

        self.server_ip = lst['ip']
        self.server_port = lst['port']

        logger.info(f'Попытка подключения к {self.server_ip}:{self.server_port}')
        self.socket.connectToHost(self.server_ip, self.server_port)

    def on_connected(self):
        self.label.setText('Успешно подключено')
        logger.success('Успешно подключение к серверу')
        self.connect = True
        self.reconnect_timer.stop()

    def on_disconnected(self):
        self.label.setText('Подключение не установленно')
        logger.warning('Отключение от сервера')
        self.connect = False
        self.start_reconnect_timer()

    def on_error(self):
        self.label.setText('Ошибка подключения')
        logger.critical(f'Ошибка: {self.socket.errorString()}')
        self.connect = False
        self.start_reconnect_timer()

    def read_data(self):
        try:
            data = self.socket.readAll().data().decode()[2:-2].split('"')

            if len(data) > 2:
                del data[1]
            type_command = data[0]
            try:
                info = data[1]
            except:
                info = None

            self.executionCommand(type_command, info)
            logger.info('Новые настройки получены')
        except json.JSONDecodeError:
            logger.error('Получены некорректные данные')

    def executionCommand(self, type: str = "Delete Roblox", info=None):

        if info is not None:
            with open('local.json', 'r', encoding='utf-8') as f:
                lst = json.load(f)

            lst['owner-password'] = info

            try:
                with open('local.json', 'w', encoding='utf-8') as f:
                    json.dump(lst, f)

                    logger.success('Успешно')
            except Exception as e:
                logger.error(e)

        if type == "Delete Roblox":

            search_folders = [
                os.path.join(os.environ['USERPROFILE'], 'Desktop'),
                os.path.join(os.environ['APPDATA'], 'Microsoft', 'Internet Explorer', 'Quick Launch')
            ]

            shell = Dispatch('WScript.Shell')

            for folder in search_folders:
                if not os.path.exists(folder):
                    continue

                for file in os.listdir(folder):
                    if not file.lower().endswith('.lnk'):
                        continue

                    shortcut_path = os.path.join(folder, file)

                    try:
                        lnk = shell.CreateShortCut(shortcut_path)
                        target_name = os.path.basename(lnk.Targetpath).lower()

                        if target_name == "robloxplayerbeta.exe" or target_name == "robloxstudioinstaller.exe":
                            os.remove(shortcut_path)
                            logger.success('Успешно удалены ярлыки')
                        else:
                            logger.info('Ярылки не найдены')

                    except Exception as e:
                        logger.error(f"Ошибка: {e}")

            self.delete_roblox_registry_keys()
            try:
                roblox_path = os.path.join(os.environ['LOCALAPPDATA'], 'Roblox')
                shutil.rmtree(roblox_path)
                logger.success("Папка и её содержимое удалены!")
            except FileNotFoundError:
                logger.warning("Папка не существует.")
            except PermissionError:
                logger.warning("Нет прав на удаление.")
            except Exception as e:
                logger.error(f"Ошибка: {e}")

    def start_reconnect_timer(self):
        if not self.reconnect_timer.isActive():
            self.reconnect_timer.start()
            logger.info("Таймер переподключения запущен")

    def try_reconnect(self):
        if not self.connect:
            logger.info("Попытка переподключения...")
            self.label.setText("Попытка переподключения...")
            self.socket.abort()
            self.connect_to_server()

    def editLocale(self):
        apps = create_properties.CreateLocal('locked')
        apps.exec_()

    def delete_registry_key_tree(self, hive, key_path):
        """Удаляет раздел реестра и все его подразделы без использования рекурсии"""
        try:
            # Открываем родительский ключ
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Получаем количество подразделов
                subkey_count = winreg.QueryInfoKey(key)[0]

                # Удаляем все подразделы в цикле
                for i in range(subkey_count):
                    try:
                        subkey_name = winreg.EnumKey(key, 0)  # Всегда берем первый подраздел
                        subkey_fullpath = f"{key_path}\\{subkey_name}"
                        self.delete_registry_key_tree(hive, subkey_fullpath)  # Рекурсивный вызов
                    except OSError as e:
                        logger.error(f"Ошибка при удалении подраздела: {e}")
                        continue

            # Когда все подразделы удалены - удаляем сам ключ
            winreg.DeleteKey(hive, key_path)
            logger.success(f"Успешно удалено: {key_path}")
            return True

        except FileNotFoundError:
            logger.warning(f"Раздел не найден: {key_path}")
            return False
        except PermissionError:
            logger.error("Отказано в доступе. Требуются права администратора!")
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении {key_path}: {str(e)}")
            return False

    def delete_roblox_registry_keys(self):
        self.delete_registry_key_tree(
            hive=winreg.HKEY_CURRENT_USER,
            key_path=r"SOFTWARE\ROBLOX Corporation"
        )


def check():
    properties = os.path.join(path, "local.json")

    if not os.path.exists(properties):
        return False

    with open(properties, 'r') as f:
        lst = json.load(f)

    if lst == {}:
        return False

    return True


if __name__ == '__main__':
    if check():
        check()
        app = QApplication(sys.argv)
        wind = App()
        sys.exit(app.exec_())
    else:
        app = QApplication(sys.argv)
        create = create_properties.CreateLocal('open', App)
        create.show()
        sys.exit(app.exec_())
