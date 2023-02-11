from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QTableWidgetItem, QTableWidget
import sys
import sqlite3


class Window(QMainWindow):
    tableWidget: QTableWidget

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("main.ui", self)

        self.build_table()

    def build_table(self):
        request = "SELECT * FROM varieties " \
                  "INNER JOIN fry ON varieties.fry_id = fry.id " \
                  "INNER JOIN state ON varieties.state_id = state.id " \
                  "INNER JOIN taste ON varieties.taste_id = taste.id"
        con = sqlite3.connect("coffee.db")
        cursor = con.cursor()
        result = cursor.execute(request).fetchall()
        print(result)

        self.tableWidget.clear()
        print(type(self.tableWidget))
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]) - 6)
        self.tableWidget.setHorizontalHeaderLabels(
            ["ID", "Название", "Прожарка",
             "Состояние", "Вкус", "Цена", "Объём"]
        )
        for i, row in enumerate(result):
            for j, elem in enumerate((0, 1, 8, 10, 12, 5, 6)):
                self.tableWidget.setItem(
                    i, j,
                    QTableWidgetItem(str(row[elem]))
                )
        self.tableWidget.resizeColumnsToContents()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
