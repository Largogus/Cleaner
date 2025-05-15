from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
from server_edit import ServerEdit
import os
import json


class CustomListWidget(QListWidget):
    def __init__(self, key: str, connect_ip: list, main_app):
        super().__init__()

        self.main_app = main_app
        self.setSelectionMode(QListWidget.SingleSelection)

        path = os.getcwd()
        self.properties = os.path.join(path, "properties.json")

        self.setIconSize(QSize(32, 32))

        self.key = key
        self.connect_ip = connect_ip

        self.update_table()

        self.itemClicked.connect(self.reference)

    def update_table(self):
        self.clear()

        with open(self.properties, 'r', encoding='utf-8') as f:
            lst = json.load(f)

        if isinstance(lst, dict):
            for info in lst[self.key]:
                if self.key == 'connected-ip':
                    item = QListWidgetItem(info[0])
                    item.setFont(QFont('Arial', 20))
                    self.addItem(item)
                    item.setData(Qt.UserRole, info[1])

                    if info[1] in self.connect_ip:
                        item.setBackground(QColor(Qt.white))
                    else:
                        item.setIcon(QIcon('img/no-connection.png'))
                        item.setBackground(QColor(255, 112, 112, 100))

                elif self.key == 'website-block':
                    item = QListWidgetItem(info)
                    item.setFont(QFont('Arial', 20))
                    self.addItem(item)

    def reference(self, item):
        data = item.data(Qt.UserRole)
        if data:
            main_window = self.window()

            if hasattr(main_window, 'send_now'):
                ref = ServerEdit(data, main_window)
            else:
                ref = ServerEdit(data, None)
            ref.exec_()

#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     wind = CustomListWidget('connected-ip')
#     wind.show()
#     sys.exit(app.exec_())