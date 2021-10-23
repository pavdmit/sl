import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from database import *
from functools import partial
from pathlib import Path

'''def resize_window(window_widget, table):
    tableWidth = 40
    for i in range(table.columnCount()):
        tableWidth += table.columnWidth(i)
    tableHight = 30 * table.rowCount()
    if tableHight > 800:
        tableHight = 800
    # window_widget.resize(tableWidth, tableHight)
    window_widget.setFixedWidth(tableWidth)
    window_widget.setFixedHeight(tableHight)
    return tableWidth, tableHight'''


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'login_window.ui')
        loadUi(path_to_ui, self)
        self.login_btn.clicked.connect(self.login_function)
        self.signup_btn.clicked.connect(self.sign_up)
        self.sign_in_dialog = None
        self.dialog_widget = None
        # pixmap = QPixmap('background.png')
        # self.label.setPixmap(pixmap)
        # self.label.update()

    def login_function(self):
        email = self.email_input.text()
        password = self.password_input.text()
        is_authorised, user_id = user_authorisation(email, password)
        if is_authorised:
            account = Account(user_id)
            widget.addWidget(account)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            self.sign_in_dialog = SignInDialog()
            self.dialog_widget = QtWidgets.QStackedWidget()
            self.dialog_widget.addWidget(self.sign_in_dialog)
            self.dialog_widget.show()

    @staticmethod
    def sign_up():
        registration_window = RegistrationWindow()
        widget.addWidget(registration_window)
        widget.setCurrentIndex(widget.currentIndex() + 1)


'''class Table(QWidget):
    def __init__(self, table_name):
        super(Table, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'table.ui')
        loadUi(path_to_ui, self)
        fill_table(self.table, table_name)'''


class ImagesLabelWindow(QWidget):
    def __init__(self):
        super(ImagesLabelWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'images_label_window.ui')
        loadUi(path_to_ui, self)


class PlainWidget:
    def __init__(self, page, workflow_name, coordinates, stackedWidget, projects_page):
        self.plain_widget = QtWidgets.QWidget(page)
        self.plain_widget.setGeometry(QtCore.QRect(coordinates[0], coordinates[1], 230, 160))
        self.plain_widget.setObjectName("plain_widget")
        self.plain_widget.setStyleSheet("")
        self.button = QtWidgets.QPushButton(self.plain_widget)
        self.button.setGeometry(QtCore.QRect(0, 0, 230, 60))
        self.button.setStyleSheet("QPushButton {\n"
                                  "    background-color: rgb(78, 0, 234);\n"
                                  "    color:rgb(243,247,254);\n"
                                  "    border: 0px solid;\n"
                                  "    font: 20pt \"Andale Mono\";\n"
                                  "    border-top-left-radius: 15px;\n"
                                  "    border-top-right-radius: 15px;\n"
                                  "}\n"
                                  "\n"
                                  "QPushButton:hover {\n"
                                  "    background-color: rgb(254, 204, 102);\n"
                                  "    color:rgb(59, 146, 212);\n"
                                  "}")
        self.button.setText(workflow_name)
        self.button.setObjectName("button")
        self.button.clicked.connect(lambda: stackedWidget.setCurrentWidget(projects_page))
        self.button.clicked.connect(is_clicked)
        self.background_frame = QtWidgets.QFrame(self.plain_widget)
        self.background_frame.setGeometry(QtCore.QRect(0, 60, 230, 100))
        self.background_frame.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                            "border-bottom-right-radius: 15px;\n"
                                            "border-bottom-left-radius:  15px;")
        self.background_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.background_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.background_frame.setObjectName("background_frame")


def is_clicked():
    print("Clicked")


class Account(QMainWindow):
    def __init__(self, user_id):
        super(Account, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'main_window.ui')
        loadUi(path_to_ui, self)
        self.user_id = user_id
        self.label_window = None
        self.window_widget = None

        # Initial window settings
        team_names = get_team_names(user_id)
        self.team_name = team_names[0]
        self.team_names_cb.addItems(team_names)
        self.team_picture.setText(self.team_name[0])
        self.workflow_names = get_team_workflows(team_names[0])
        self.workspace_name = self.workflow_names[0]
        self.workspace_names_cb.addItems(self.workflow_names)
        self.workspace_picture.setText(self.workspace_name[0])
        fill_members(self.members_table, self.team_name)
        fill_projects(self.datasets_table, self.workspace_name)
        self.datasets_table.selectionModel().selectionChanged.connect(self.open_editor)

        # Changing workflow and team if changed
        self.team_names_cb.activated[str].connect(self.change_session_settings)
        self.workspace_names_cb.activated[str].connect(self.change_session_settings)

        # Changing workspace window
        self.fill_workspaces()

        # Pages buttons
        self.workspaces_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.workspaces_page))
        self.members_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.members_page))
        self.files_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.files_page))
        self.projects_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.projects_page))
        self.tasks_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.tasks_page))
        self.signout_btn1.clicked.connect(self.sign_out)
        self.signout_btn2.clicked.connect(self.sign_out)
        self.signout_btn3.clicked.connect(self.sign_out)
        self.signout_btn4.clicked.connect(self.sign_out)
        self.signout_btn5.clicked.connect(self.sign_out)

    '''def show_table(self, table_name=None):
        self.TableWindow = Table(table_name)
        self.widget2 = QtWidgets.QStackedWidget()
        self.widget2.addWidget(self.TableWindow)
        resize_window(self.widget2, self.TableWindow.table)
        self.widget2.show()'''

    # move to database
    def fill_workspaces(self):
        bottom_margin = 100
        count = 0
        for i in range((len(self.workflow_names) // 3) + 1):
            left_margin = 25
            for j in range(3):
                plain_widget = PlainWidget(self.workspaces_page, self.workflow_names[count],
                                           [left_margin, bottom_margin],
                                           self.stackedWidget, self.projects_page)
                left_margin += 255
                count += 1
                if count >= len(self.workflow_names):
                    break
            bottom_margin += 185

    def open_editor(self):
        self.label_window = ImagesLabelWindow()
        self.window_widget = QtWidgets.QStackedWidget()
        self.window_widget.addWidget(self.label_window)
        self.window_widget.show()

    def change_session_settings(self):
        self.team_name = self.team_names_cb.currentText()
        self.workspace_name = self.workspace_names_cb.currentText()
        self.team_picture.setText(self.team_name[0])
        self.workspace_picture.setText(self.workspace_name[0])
        fill_members(self.members_table, self.team_name)
        fill_projects(self.datasets_table, self.workspace_name)
        self.fill_workspaces()

    @staticmethod
    def sign_out():
        back_to_login = Login()
        widget.addWidget(back_to_login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class RegistrationWindow(QWidget):
    def __init__(self):
        super(RegistrationWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'signup_window.ui')
        loadUi(path_to_ui, self)
        self.ahacc_btn.clicked.connect(self.close_window)
        self.create_acc_btn.clicked.connect(lambda:
                                            register(self.email_input_line.text(), self.password_input_line.text(),
                                                     self.fname_input_line.text(), self.phnumber_input_line.text(),
                                                     self.lname_input_line.text(), self.gender_input_line.text()))
        self.create_acc_btn.clicked.connect(self.close_window)

    @staticmethod
    def close_window():
        back_to_login = Login()
        widget.addWidget(back_to_login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class SignInDialog(QDialog):
    def __init__(self):
        super(SignInDialog, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'dialog_window.ui')
        loadUi(path_to_ui, self)
        # self.ok_btn.clicked.connect(self.close_window)

    def close_window(self):
        pass


app = QApplication(sys.argv)
MainWindow = Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(MainWindow)
widget.show()
app.exec_()
