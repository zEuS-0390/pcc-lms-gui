from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout, QGridLayout,
    QHBoxLayout, QLineEdit,
    QLabel, QPushButton,
    QComboBox
)
import logging
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
try:
    from db.manager import Manager
    from db.tables import *
    import rc.resources
except ModuleNotFoundError:
    import sys, os
    sys.path.insert(0, os.path.dirname(sys.path[0]))
    from configparser import ConfigParser
    from src.constants import CONFIG_NAME
    from db.manager import Manager
    from db.tables import *
    import rc.resources

class NewStudent(QWidget):

    update_list = pyqtSignal()

    def __init__(self, db: Manager, parent=None):
        super(NewStudent, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.db = db
        self.setup_UI()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key.Key_Return:
            self.add()
        elif key_event.key() == Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(key_event)

    def setup_UI(self):
        self.setWindowIcon(QIcon(":/new_student.png"))
        self.setWindowTitle("Add New Student")
        self.mainlayout = QVBoxLayout()
        self.inputslayout = QGridLayout()
        self.btnslayout = QHBoxLayout()
        self.setup_inputs()
        self.setup_btns()
        self.setLayout(self.mainlayout)
        self.resize(self.mainlayout.sizeHint())

    def setup_inputs(self):
        self.inputs_conf = {
            "fname": ("First Name:", QLineEdit),
            "mname": ("Middle Name:", QLineEdit),
            "lname": ("Last Name:", QLineEdit),
            "gender": ("Gender:", QComboBox),
            "age": ("Age:", QLineEdit)
        }
        self.inputs = {}
        row = 0
        col = 0
        for name, val in self.inputs_conf.items():
            obj = None
            col = 0
            label = QLabel(val[0])
            col += 1
            if val[1] == QLineEdit:
                obj = val[1]()
            elif val[1] == QComboBox:
                obj = val[1]()
            self.inputslayout.addWidget(label, row, col)
            col += 1
            self.inputslayout.addWidget(obj, row, col)
            self.inputs[name] = (label, obj)
            row += 1
        self.mainlayout.addLayout(self.inputslayout)

        self.inputs["gender"][1].addItem("Male")
        self.inputs["gender"][1].addItem("Female")

    def setup_btns(self):
        self.btns_conf = {
            "cancel": ("Cancel", self.close),
            "submit": ("Add", self.add)
        }
        self.btns = {}
        for name, val in self.btns_conf.items():
            btn = QPushButton(val[0])
            btn.clicked.connect(val[1])
            self.btnslayout.addWidget(btn)
            self.btns[name] = btn
        self.mainlayout.addLayout(self.btnslayout)

    def add(self):
        student = Student(
            fname=self.inputs["fname"][1].text(), 
            mname=self.inputs["mname"][1].text(), 
            lname=self.inputs["lname"][1].text(),
            gender=self.inputs["gender"][1].currentText(),
            age=int(self.inputs["age"][1].text())
        )
        self.db.session.add(student)
        self.db.session.commit()
        self.db.session.close()
        self.update_list.emit()
        logging.info("Student '{fname}' has successfully been added.".format(fname=self.inputs["fname"][1].text()))
        self.close()

if __name__=="__main__":
    parser = ConfigParser()
    parser.read("cfg/app.cfg")
    manager = Manager(parser)
    app = QApplication(sys.argv)
    widget = NewStudent(manager)
    widget.show()
    sys.exit(app.exec())