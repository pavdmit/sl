import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from PyQt5.uic import loadUi
from database import *
from functools import partial
from pathlib import Path
import os

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtGui import QBrush, QImage, QPainter, QPen
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon


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


class ImagesLabelWindow(QWidget):
    def __init__(self, dataset_name):
        super(ImagesLabelWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'images_label_window.ui')
        loadUi(path_to_ui, self)
        fill_files_in_dataset(self.list_of_files, dataset_name)
        self.dataset_name = dataset_name
        self.list_of_files.setColumnWidth(0, 240)
        self.drawing = False
        self.list_of_files.selectionModel().selectionChanged.connect(
            lambda: fill_image_file_params(self.list_of_files.currentItem().text(), self.picture, self.x1_input,
                                           self.y1_input, self.x2_input, self.y2_input, self.class_input))
        self.save_btn.clicked.connect(lambda: save_image_changes(self.list_of_files.currentItem().text(), self.x1_input,
                                                                 self.y1_input, self.x2_input, self.y2_input,
                                                                 self.class_input))
        self.save_btn.clicked.connect(
            lambda: fill_image_file_params(self.list_of_files.currentItem().text(), self.picture, self.x1_input,
                                           self.y1_input, self.x2_input, self.y2_input, self.class_input))
        self.addnew_btn.clicked.connect(self.open_file)
        self.import_to_csv_btn.clicked.connect(lambda: import_to_csv(dataset_name))
        self.import_to_excel_btn.clicked.connect(lambda: import_to_excel(dataset_name))

    def open_file(self):
        try:
            file_name = QFileDialog.getOpenFileName()
            path = file_name[0]
            file_name = os.path.basename(path)
            save_image_to_dataset(file_name, self.dataset_name)
            fill_files_in_dataset(self.list_of_files, self.dataset_name)
        except:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.x1_input.setText(str(event.pos().x() - 35))
            self.y1_input.setText(str(event.pos().y() - 35))

    def mouseMoveEvent(self, event):
        if event.button() == Qt.NoButton:
            self.x2_input.setText(str(event.pos().x() - 35))
            self.y2_input.setText(str(event.pos().y() - 35))
            save_image_changes(self.list_of_files.currentItem().text(), self.x1_input,
                               self.y1_input, self.x2_input, self.y2_input,
                               self.class_input)
            fill_image_file_params(self.list_of_files.currentItem().text(), self.picture, self.x1_input,
                                   self.y1_input, self.x2_input, self.y2_input, self.class_input)


class TextLabelWindow(QWidget):
    def __init__(self, dataset_name):
        super(TextLabelWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'texts_label_window.ui')
        loadUi(path_to_ui, self)
        self.dataset_name = dataset_name
        files_names = get_text_files_names(self.dataset_name)
        self.texts_list.addItems(files_names)
        fill_text_label_elements(self.list_of_labels, self.text, self.texts_list.currentText())
        self.texts_list.activated[str].connect(lambda: fill_text_label_elements(self.list_of_labels, self.text,
                                                                                self.texts_list.currentText()))
        self.text.selectionChanged.connect(lambda: self.fill_fields())
        self.addnew_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(lambda: save_text_label(self.texts_list.currentText(),
                                                              self.text_fragment_input,
                                                              self.position_input, self.label_input))
        self.save_btn.clicked.connect(lambda: fill_text_label_elements(self.list_of_labels,
                                                                       self.text,
                                                                       self.texts_list.currentText()))
        self.delete_btn.clicked.connect(lambda: delete_text_label(self.list_of_labels.currentItem().text()))
        self.delete_btn.clicked.connect(lambda: fill_text_label_elements(self.list_of_labels,
                                                                         self.text,
                                                                         self.texts_list.currentText()))

    def open_file(self):
        try:
            file_name = QFileDialog.getOpenFileName()
            path = file_name[0]
            file_name = os.path.basename(path)
            with open(path) as f:
                file = f.readlines()
            add_text_file(file_name, file[0], self.dataset_name)
            added_file_name = get_text_files_names(self.dataset_name)
            added_file_name = added_file_name[-1]
            self.texts_list.addItem(added_file_name)
        except:
            pass

    def fill_fields(self):
        text = self.text.toPlainText()
        cursor = self.text.textCursor()
        self.text_fragment_input.setText(text[cursor.selectionStart():cursor.selectionEnd()])
        self.position_input.setText(str(cursor.selectionStart()))


class AddProject(QWidget):
    def __init__(self, workspace_name):
        super(AddProject, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'add_project_dialog.ui')
        loadUi(path_to_ui, self)
        self.save_btn.clicked.connect(self.add_project)

    def add_project(self):
        add_dataset(self.dataset_name_input.text(), self.task_type_input.text(), self.description_input.text())


class InviteWindow(QWidget):
    def __init__(self, team_name):
        super(InviteWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'invite_dialog.ui')
        loadUi(path_to_ui, self)
        self.invite_btn.setShortcut('Ctrl+Return')


class EditAccountWindow(QWidget):
    def __init__(self, user_id):
        super(EditAccountWindow, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'edit_account.ui')
        loadUi(path_to_ui, self)
        account_data = load_user_account(user_id)
        self.email_edit_line.setText(account_data[0])
        self.password_edit_line.setText(account_data[5])
        self.fname_edit_line.setText(account_data[1])
        self.phnumber_edit_line.setText(account_data[2])
        self.lname_edit_line.setText(account_data[3])
        self.gender_edit_line.setText(account_data[4])
        self.save_changes_btn.clicked.connect(
            lambda: save_account_changes(user_id, self.email_edit_line, self.password_edit_line,
                                         self.fname_edit_line, self.phnumber_edit_line, self.lname_edit_line,
                                         self.gender_edit_line))


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
        self.button.clicked.connect(lambda: Account.is_clicked(workflow_name=workflow_name))
        self.background_frame = QtWidgets.QFrame(self.plain_widget)
        self.background_frame.setGeometry(QtCore.QRect(0, 60, 230, 100))
        self.background_frame.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                            "border-bottom-right-radius: 15px;\n"
                                            "border-bottom-left-radius:  15px;")
        self.background_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.background_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.background_frame.setObjectName("background_frame")


class Account(QMainWindow):
    def __init__(self, user_id):
        super(Account, self).__init__()
        path_to_ui = Path(Path.cwd(), 'uis', 'main_window.ui')
        loadUi(path_to_ui, self)
        self.user_id = user_id
        self.label_window = None
        self.window_widget = None
        self.edit_window = None
        self.invite_window = None
        self.add_window = None
        user_data = load_user_account(user_id)
        self.user_photo1.setText(str(user_data[1][0] + user_data[3][0]))
        self.user_photo2.setText(str(user_data[1][0] + user_data[3][0]))
        self.user_photo3.setText(str(user_data[1][0] + user_data[3][0]))
        self.user_photo4.setText(str(user_data[1][0] + user_data[3][0]))
        self.user_photo5.setText(str(user_data[1][0] + user_data[3][0]))

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
        fill_image_files(self.image_files_table, self.workspace_name)
        fill_text_files(self.text_files_table, self.workspace_name)
        self.image_files_table.setColumnWidth(0, 300)
        self.image_files_table.setColumnWidth(1, 280)
        self.text_files_table.setColumnWidth(0, 150)
        self.text_files_table.setColumnWidth(1, 350)
        self.text_files_table.setColumnWidth(2, 350)
        self.datasets_table.setColumnWidth(0, 250)
        self.datasets_table.setColumnWidth(1, 250)
        self.datasets_table.setColumnWidth(2, 259)
        self.members_table.setColumnWidth(0, 190)
        self.members_table.setColumnWidth(1, 190)
        self.members_table.setColumnWidth(2, 379)
        self.datasets_table.selectionModel().selectionChanged.connect(
            lambda: self.open_editor(self.datasets_table.currentItem().text()))
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
        self.signout_btn1.setShortcut("Ctrl+X")
        self.signout_btn2.clicked.connect(self.sign_out)
        self.signout_btn3.clicked.connect(self.sign_out)
        self.signout_btn4.clicked.connect(self.sign_out)
        self.signout_btn5.clicked.connect(self.sign_out)
        self.edit_btn1.clicked.connect(self.edit_account)
        self.edit_btn2.clicked.connect(self.edit_account)
        self.edit_btn3.clicked.connect(self.edit_account)
        self.edit_btn4.clicked.connect(self.edit_account)
        self.edit_btn5.clicked.connect(self.edit_account)
        self.invite_btn.clicked.connect(self.invite_user)
        self.search_btn.clicked.connect(lambda: fill_image_files(self.image_files_table, self.workspace_name,
                                                                 self.search_line.text()))
        self.search_btn.clicked.connect(lambda: fill_text_files(self.text_files_table, self.workspace_name,
                                                                self.search_line.text()))
        self.add_proj_btn.clicked.connect(self.add_project)

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

    def edit_account(self):
        self.edit_window = EditAccountWindow(self.user_id)
        self.window_widget = QtWidgets.QStackedWidget()
        self.window_widget.addWidget(self.edit_window)
        self.window_widget.show()

    def add_project(self):
        self.add_window = AddProject(self.workspace_name)
        self.window_widget = QtWidgets.QStackedWidget()
        self.window_widget.addWidget(self.add_window)
        self.window_widget.show()
        fill_projects(self.datasets_table, self.workspace_name)

    def open_editor(self, dataset_name):
        task_type = which_task_type(dataset_name)
        if task_type == 'image_classification':
            self.label_window = ImagesLabelWindow(dataset_name)
            self.window_widget = QtWidgets.QStackedWidget()
            self.window_widget.addWidget(self.label_window)
            self.window_widget.show()
        elif task_type == 'text_classification':
            self.label_window = TextLabelWindow(dataset_name)
            self.window_widget = QtWidgets.QStackedWidget()
            self.window_widget.addWidget(self.label_window)
            self.window_widget.show()

    def invite_user(self):
        self.invite_window = InviteWindow(self.team_name)
        self.window_widget = QtWidgets.QStackedWidget()
        self.window_widget.addWidget(self.invite_window)
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
    def is_clicked(workflow_name):
        print("Clicked: ", workflow_name)

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


app = QApplication(sys.argv)
MainWindow = Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(MainWindow)
widget.show()
app.exec_()
