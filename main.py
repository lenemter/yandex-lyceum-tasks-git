import sqlite3
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from MainWindow import Ui_MainWindow as main
from AddEditCoffeeForm import Ui_MainWindow as form


class Coffee(QMainWindow, main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("data/coffee.sqlite")
        self.pushButton.clicked.connect(self.switch_to_add_edit_form)
        self.pushButton_2.clicked.connect(self.select_data)
        self.select_data()

    def select_data(self):
        cur = self.connection.cursor()
        result = cur.execute("""SELECT * FROM Coffee""").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def switch_to_add_edit_form(self):
        self.form = AddEditForm()
        self.form.show()


class AddEditForm(QMainWindow, form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("data/coffee.sqlite")
        self.pushButton.clicked.connect(self.add_new_data)
        self.pushButton_2.clicked.connect(self.save_results)
        self.pushButton_3.clicked.connect(self.select_data)
        self.pushButton_4.clicked.connect(self.save_added)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.modified = {}
        self.titles = None

    def select_data(self):
        cur = self.connection.cursor()
        item_id = self.spinBox.text()
        result = cur.execute("SELECT * FROM Coffee WHERE id=?", (item_id,)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            cur = self.connection.cursor()
            que = "UPDATE Coffee SET "
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += f" WHERE id = ?"
            cur.execute(que, (self.spinBox.text(),))
            self.connection.commit()
            self.modified.clear()
            self.window().close()

    def switch_to_main_window(self):
        self.main = Coffee()
        self.main.show()

    def add_new_data(self):
        cur = self.connection.cursor()
        counter = cur.execute("SELECT * FROM Coffee").fetchall()
        self.id = len(counter)
        result = cur.execute("SELECT * FROM Coffee WHERE id=?", (1,)).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str('Введите данные')))
        self.modified = {}

    def item_changed_add(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_added(self):
        if self.modified:
            cur = self.connection.cursor()
            keys = [self.modified.get(key) for key in self.modified.keys()]
            helper = [x for x in self.modified.keys()]
            que = f"INSERT INTO Coffee({', '.join(helper)}) VALUES" \
                  f"({', '.join([self.modified.get(key) for key in self.modified.keys()])})"
            cur.execute(que)
            self.connection.commit()
            self.modified.clear()
            self.window().close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec())
