import PIL
from PyQt5.QtWidgets import QTableWidgetItem
import psycopg2
from random import randint
from PIL.ImageQt import ImageQt
from PIL.Image import Image
import io
import base64
from PyQt5.QtGui import QPixmap
from pathlib import Path
from PIL import Image, ImageDraw

con = psycopg2.connect(
    database="dataset_marker",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cur = con.cursor()


def register(email, password, first_name, phone_number, last_name, gender):
    cur.execute("INSERT INTO users VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(email, first_name, phone_number,
                                                                                       last_name, gender,
                                                                                       str(randint(100, 200)),
                                                                                       password))

    con.commit()


def load_user_account(user_id):
    cur.execute("SELECT email, first_name, phone_number, last_name, gender, password FROM users WHERE id = '{}'".format(
        user_id))
    account_data = cur.fetchall()
    account_data = [account_data[0][i] for i in range(len(account_data[0]))]
    return account_data


def save_account_changes(user_id, email_edit_line, password_edit_line, fname_edit_line, phnumber_edit_line,
                         lname_edit_line, gender_edit_line):
    email = str(email_edit_line.text())
    password = str(password_edit_line.text())
    first_name = str(fname_edit_line.text())
    phone_number = str(phnumber_edit_line.text())
    last_name = str(lname_edit_line.text())
    gender = str(gender_edit_line.text())
    cur.execute("UPDATE users SET email='{}', first_name='{}', phone_number='{}', last_name='{}', gender='{}', "
                "password= '{}' WHERE id='{}'".format(email, first_name, phone_number, last_name, gender, password,
                                                      user_id))
    con.commit()


def fill_text_label_elements(texts_list, list_of_labels, text_label, dataset_name):
    cur.execute("SELECT file_name FROM dataset_to_file WHERE dataset_name = '{}'".format(dataset_name))
    file_names = cur.fetchall()
    file_names = [file_names[i][0] for i in range(len(file_names))]
    if len(file_names) == 0:
        file_names.append("No texts")
    texts_list.clear()
    texts_list.addItems(file_names)
    cur.execute("SELECT text_fragment, label FROM text_files WHERE file_name = '{}'".format(file_names[0]))
    label_with_text = cur.fetchall()
    if len(label_with_text) == 0:
        label_with_text.append(("No text", "No label"))
    list_of_labels.setColumnCount(len(label_with_text[0]))
    list_of_labels.setHorizontalHeaderLabels(['Text', 'Label'])
    list_of_labels.setRowCount(len(label_with_text))
    k = 0
    for row in label_with_text:
        for i in range(len(row)):
            list_of_labels.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    list_of_labels.verticalHeader().setVisible(False)
    if label_with_text[0] != ("No text", "No label"):
        cur.execute("SELECT text FROM text_files WHERE file_name = '{}'".format(file_names[0]))
        text = cur.fetchall()
        text = text[0][0]
        text_label.setText(text)
    return file_names[0]


def save_text_label(file_name, text_fragment_input, label_input):
    cur.execute("INSERT INTO text_files VALUES ('{}','{}','{}','{}')".format(file_name, '', label_input.text(),
                                                                             text_fragment_input.text()))
    text_fragment_input.setText("")
    label_input.setText("")
    con.commit()


def add_text_label():
    pass


def delete_text_label(text_fragment_to_delete):
    cur.execute("DELETE FROM text_files WHERE text_fragment = '{}'".format(text_fragment_to_delete))
    con.commit()


def fill_image_files():
    pass


def fill_text_files():
    pass


def fill_files_in_dataset(table_obj, dataset_name):
    cur.execute("SELECT file_name FROM dataset_to_file WHERE dataset_name = '{}'".format(dataset_name))
    file_names = cur.fetchall()
    if len(file_names) == 0:
        file_names.append(("No files",))
    table_obj.setColumnCount(len(file_names[0]))
    table_obj.setHorizontalHeaderLabels(['File names'])
    table_obj.setRowCount(len(file_names))
    k = 0
    for row in file_names:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)


def which_task_type(dataset_name):
    cur.execute("SELECT task_type FROM datasets WHERE dataset_name = '{}'".format(dataset_name))
    task_type = cur.fetchall()
    task_type = task_type[0][0]
    return task_type


def user_authorisation(login, password):
    cur.execute("SELECT id FROM users WHERE email = '{}' AND password = '{}'".format(login, password))
    authorised = False
    login_data = cur.fetchall()
    for element in login_data:
        authorised = True
    return authorised, login_data[0][0]


def get_team_names(user_id):
    cur.execute("SELECT team_name FROM team_to_user WHERE user_id = '{}'".format(user_id))
    team_names = cur.fetchall()
    team_names = [team_names[i][0] for i in range(len(team_names))]
    return team_names


def get_team_workflows(current_team):
    cur.execute("SELECT workspace_name FROM workspace_to_team WHERE team_name = '{}'".format(current_team))
    workflow_names = cur.fetchall()
    workflow_names = [workflow_names[i][0] for i in range(len(workflow_names))]
    return workflow_names


def fill_image_file_params(file_name, picture, x1_input, y1_input, x2_input, y2_input, class_input):
    cur.execute("SELECT x1, y1, x2, y2, class, image_represention FROM image_files WHERE file_name = '{}'".format(file_name))
    file_params = cur.fetchall()
    file_params = [file_params[0][i] for i in range(len(file_params[0]))]
    x1_input.setText(str(file_params[0]))
    y1_input.setText(str(file_params[1]))
    x2_input.setText(str(file_params[2]))
    y2_input.setText(str(file_params[3]))
    class_input.setText(str(file_params[4]))
    image_root = path_to_ui = Path(Path.cwd(), 'data', file_name)
    image = PIL.Image.open(image_root)
    draw = ImageDraw.Draw(image)
    draw.line(
        xy=(
            (20, 100),
            (20, 40)
        ), fill='red', width=3)
    q_image = ImageQt(image)
    pixmap = QPixmap.fromImage(q_image)
    picture.setPixmap(pixmap)


def fill_members(table_obj, team_name):
    cur.execute("SELECT first_name, last_name,email FROM users WHERE id in (select user_id from team_to_user  where "
                "team_name = '{}');".format(team_name))
    members = cur.fetchall()
    table_obj.setColumnCount(len(members[0]))
    table_obj.setHorizontalHeaderLabels(['First name', 'Last name', 'Email'])
    table_obj.setRowCount(len(members))
    k = 0
    for row in members:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)


def fill_projects(table_obj, workspace_name):
    cur.execute("SELECT dataset_name, task_type, description FROM datasets WHERE dataset_name in (select "
                "dataset_name from dataset_to_workspace where workspace_name = '{}')".format(workspace_name))
    datasets = cur.fetchall()
    if len(datasets) == 0:
        datasets.append(('No datasets', ' ', ' '))
    table_obj.setColumnCount(len(datasets[0]))
    table_obj.setHorizontalHeaderLabels(['Dataset name', 'Task type', 'Description'])
    table_obj.setRowCount(len(datasets))
    k = 0
    for row in datasets:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)
