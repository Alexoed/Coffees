from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QTableWidgetItem, QTableWidget, QPushButton, QComboBox, QLineEdit, \
    QSpinBox
from UI.main import Ui_Form as Main_window_ui
from UI.addEditCoffeeForm import Ui_Form as Sub_window_ui

import sys
import sqlite3


class Window(QMainWindow, Main_window_ui):
    tableWidget: QTableWidget
    add_button: QPushButton

    def __init__(self):
        super(Window, self).__init__()
        # uic.loadUi("UI/main.ui", self)
        self.setupUi(self)

        self.add_button.clicked.connect(self.open)
        self.add_button.setToolTip("Выберите запись для изменения, "
                                   "отмените выделение для добавления.")

        self.build_table()

    def open(self):
        selected = self.tableWidget.selectedItems()
        index = None
        if any(selected):
            index = self.tableWidget.item(selected[0].row(), 0).text()
        self.adder = ExWindow(self, index)
        self.adder.show()

    def build_table(self):
        self.tableWidget.clear()
        request = "SELECT * FROM varieties " \
                  "INNER JOIN fry ON varieties.fry_id = fry.id " \
                  "INNER JOIN state ON varieties.state_id = state.id " \
                  "INNER JOIN taste ON varieties.taste_id = taste.id"
        con = sqlite3.connect("data/coffee.db")
        cursor = con.cursor()
        result = cursor.execute(request).fetchall()
        # print(result)

        self.tableWidget.clear()
        # print(type(self.tableWidget))
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]) - 6)
        self.tableWidget.setHorizontalHeaderLabels(
            ["ID", "Название", "Прожарка",
             "Состояние", "Вкус", "Цена", "Масса"]
        )
        for i, row in enumerate(result):
            for j, elem in enumerate((0, 1, 8, 10, 12, 5, 6)):
                self.tableWidget.setItem(
                    i, j,
                    QTableWidgetItem(str(row[elem]))
                )
        self.tableWidget.resizeColumnsToContents()


class ExWindow(QMainWindow, Sub_window_ui):
    fry_box: QComboBox
    state_box: QComboBox
    taste_box: QComboBox
    name_line: QLineEdit
    done_button: QPushButton
    price_box: QSpinBox
    mass_box: QSpinBox

    def __init__(self, caller, index):
        super(ExWindow, self).__init__()
        self.caller = caller
        # uic.loadUi("UI/addEditCoffeeForm.ui", self)
        self.setupUi(self)

        con = sqlite3.connect("data/coffee.db")
        cursor = con.cursor()

        self.index = index

        self.param_fry = {}
        for value, key in cursor.execute(
                "SELECT * FROM fry").fetchall():
            self.param_fry[key] = value
        self.fry_box.addItems(list(self.param_fry.keys()))

        self.param_state = {}
        for value, key in cursor.execute(
                "SELECT * FROM state").fetchall():
            self.param_state[key] = value
        self.state_box.addItems(list(self.param_state.keys()))

        self.param_taste = {}
        for value, key in cursor.execute(
                "SELECT * FROM taste").fetchall():
            self.param_taste[key] = value
        self.taste_box.addItems(list(self.param_taste.keys()))

        if index is None:
            self.done_button.clicked.connect(self.add)
        else:
            self.done_button.clicked.connect(self.edit)
            request = f"SELECT * FROM varieties WHERE id = {index}"
            result = cursor.execute(request).fetchone()
            self.name_line.setText(result[1])
            self.fry_box.setCurrentIndex(result[2])
            self.state_box.setCurrentIndex(result[3])
            self.taste_box.setCurrentIndex(result[4])
            self.price_box.setValue(result[5])
            self.mass_box.setValue(result[6])

    def add(self):
        fry_id = self.param_fry[self.fry_box.currentText()]
        state_id = self.param_state[self.state_box.currentText()]
        taste_id = self.param_taste[self.taste_box.currentText()]
        request = "INSERT INTO varieties(name, fry_id, state_id, " \
                  "taste_id, price, pack_size) " \
                  f"VALUES('{self.name_line.text()}', " \
                  f"{fry_id}, {state_id}, {taste_id}, " \
                  f"{self.price_box.text()}, {self.mass_box.text()})"

        con = sqlite3.connect("data/coffee.db")
        cursor = con.cursor()
        cursor.execute(request)
        con.commit()
        self.caller.build_table()
        self.close()

    def edit(self):
        fry_id = self.param_fry[self.fry_box.currentText()]
        state_id = self.param_state[self.state_box.currentText()]
        taste_id = self.param_taste[self.taste_box.currentText()]
        request = f"UPDATE varieties " \
                  f"SET name = '{self.name_line.text()}', " \
                  f"fry_id = {fry_id}, " \
                  f"state_id = {state_id}," \
                  f"taste_id = {taste_id} " \
                  f"WHERE id = {self.index}"

        con = sqlite3.connect("data/coffee.db")
        cursor = con.cursor()
        cursor.execute(request)
        con.commit()
        self.caller.build_table()
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
