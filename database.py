import PIL
from PyQt5.QtWidgets import QTableWidgetItem
import psycopg2
from random import randint
from PIL.ImageQt import ImageQt
from PIL.Image import Image
import csv
import xlsxwriter
from PyQt5.QtGui import QPixmap
from pathlib import Path
from PIL import Image, ImageDraw

con = psycopg2.connect(
    database="sl",
    user="postgres",
    password="postgres",
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


def get_text_files_names(dataset_name):
    cur.execute("SELECT file_name FROM dataset_to_file WHERE dataset_name = '{}'".format(dataset_name))
    file_names = cur.fetchall()
    file_names = [file_names[i][0] for i in range(len(file_names))]
    if len(file_names) == 0:
        file_names.append("No texts")
    return file_names


def fill_text_label_elements(list_of_labels, text_label, current_file_name):
    cur.execute("SELECT text_fragment, label, position FROM text_files_labels WHERE file_name = '{}'".format(current_file_name))
    label_with_text = cur.fetchall()
    if len(label_with_text) == 0:
        label_with_text.append(("No text", "No label", "No pos"))
    list_of_labels.setColumnCount(len(label_with_text[0]))
    list_of_labels.setHorizontalHeaderLabels(['Text', 'Label', 'Pos'])
    list_of_labels.setRowCount(len(label_with_text))
    k = 0
    for row in label_with_text:
        for i in range(len(row)):
            list_of_labels.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    list_of_labels.verticalHeader().setVisible(False)
    cur.execute("SELECT text FROM text_files WHERE file_name = '{}'".format(current_file_name))
    text = cur.fetchall()
    text = text[0][0]
    text_label.setText(text)


def save_text_label(file_name, text_fragment_input, position_input, label_input):
    cur.execute("INSERT INTO text_files_labels VALUES ('{}','{}','{}','{}')".format(file_name,
                                                                                    text_fragment_input.text(),
                                                                                    label_input.text(),
                                                                                    position_input.text()))
    text_fragment_input.setText("")
    label_input.setText("")
    position_input.setText("")
    con.commit()


def add_text_file(file_name, file, dataset_name):
    cur.execute("INSERT INTO text_files VALUES ('{}','{}','{}','{}')".format(file_name, file, '', ''))
    cur.execute(
        "INSERT INTO dataset_to_file VALUES ( '{}', '{}')".format(file_name, dataset_name))
    con.commit()


def delete_text_label(text_fragment_to_delete):
    cur.execute("DELETE FROM text_files_labels WHERE text_fragment = '{}'".format(text_fragment_to_delete))
    con.commit()


def add_dataset(dataset_name_input, task_type_input, description_input):  # TODO
    pass


def import_to_csv(dataset_name, file_name="output.csv"):
    cur.execute("SELECT file_name, x1, y1, x2, y2, class, image_width, image_height FROM image_files WHERE file_name "
                "IN (SELECT file_name FROM dataset_to_file WHERE dataset_name = '{}')".format(dataset_name))
    image_data = cur.fetchall()
    header = ['file_name', 'x1', 'y1', 'x2', 'y2', 'class', 'image_width', 'image_height']
    file_path = Path(Path.cwd(), 'output data', file_name)
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(image_data)


def import_to_excel(dataset_name, file_name="output.xlsx"):
    cur.execute("SELECT file_name, x1, y1, x2, y2, class, image_width, image_height FROM image_files WHERE file_name "
                "IN (SELECT file_name FROM dataset_to_file WHERE dataset_name = '{}')".format(dataset_name))
    image_data = cur.fetchall()
    file_path = Path(Path.cwd(), 'output data', file_name)
    file = xlsxwriter.Workbook(file_path)
    worksheet = file.add_worksheet("Image data")
    row = 0
    for elem in image_data:
        worksheet.write(row, 0, elem[0])
        worksheet.write(row, 1, elem[1])
        worksheet.write(row, 2, elem[2])
        worksheet.write(row, 3, elem[3])
        worksheet.write(row, 4, elem[4])
        worksheet.write(row, 5, elem[5])
        worksheet.write(row, 6, elem[6])
        worksheet.write(row, 7, elem[7])
        row += 1
    file.close()


def fill_image_files(table_obj, workspace_name, query=None):
    if query is not None:
        split_query = query.split()
        if len(split_query) != 4:
            for i in range(4 - len(split_query)):
                split_query.append(" ")
        if split_query[2] == ' ':
            split_query[2] = '0'
        if split_query[3] == ' ':
            split_query[3] = '0'
        cur.execute("SELECT file_name, class, image_width, image_height FROM image_files "
                    "WHERE file_name LIKE '%{}%' OR class LIKE '%{}%' OR image_width = {} OR image_height = {} "
                    "AND file_name IN (SELECT file_name FROM dataset_to_file WHERE dataset_name in "
                    "(SELECT dataset_name FROM dataset_to_workspace WHERE workspace_name = '{}'))".format(
            split_query[0], split_query[1],
            split_query[2], split_query[3],
            workspace_name))
    else:
        cur.execute("SELECT file_name, class, image_width, image_height FROM image_files WHERE file_name IN (SELECT "
                    "file_name FROM dataset_to_file WHERE dataset_name in (SELECT dataset_name FROM "
                    "dataset_to_workspace WHERE workspace_name = '{}'))".format(workspace_name))
    image_data = cur.fetchall()
    if len(image_data) == 0:
        image_data.append(("No files", "", "", ""))
    table_obj.setColumnCount(len(image_data[0]))
    table_obj.setHorizontalHeaderLabels(['File names', 'Class', 'Width', 'Height'])
    table_obj.setRowCount(len(image_data))
    k = 0
    for row in image_data:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)


def fill_text_files(table_obj, workspace_name, query=None):
    if query is not None:
        split_query = query.split()
        if len(split_query) != 3:
            for i in range(3 - len(split_query)):
                split_query.append(" ")
        cur.execute("SELECT file_name, label, text_fragment FROM text_files WHERE file_name LIKE '%{}%' OR "
                    "label LIKE '%{}%' OR text_fragment LIKE '%{}%' AND file_name IN (SELECT file_name FROM "
                    "dataset_to_file WHERE dataset_name in (SELECT dataset_name FROM dataset_to_workspace "
                    "WHERE workspace_name = '{}'))".format(split_query[0], split_query[1], split_query[2],
                                                           workspace_name))
    else:
        cur.execute("SELECT file_name, label, text_fragment FROM text_files WHERE file_name IN (SELECT "
                    "file_name FROM dataset_to_file WHERE dataset_name in "
                    "(SELECT dataset_name FROM dataset_to_workspace WHERE workspace_name = '{}'))".format(
            workspace_name))
    text_data = cur.fetchall()
    if len(text_data) == 0:
        text_data.append(("No files", "", ""))
    table_obj.setColumnCount(len(text_data[0]))
    table_obj.setHorizontalHeaderLabels(['File names', 'Label', 'Text fragment'])
    table_obj.setRowCount(len(text_data))
    k = 0
    for row in text_data:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)


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


def save_image_to_dataset(file_name, dataset_name):
    image_class = "Unknown"
    path_to_file = Path(Path.cwd(), 'data', file_name)
    with Image.open(path_to_file) as image:
        width, height = image.size
    cur.execute(
        "INSERT INTO image_files VALUES ( '{}', '{}', '{}','{}','{}','{}','{}','{}')".format(
            file_name, 0, 0, 0, 0, image_class, width, height))
    cur.execute(
        "INSERT INTO dataset_to_file VALUES ( '{}', '{}')".format(file_name, dataset_name))
    con.commit()


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
    if len(team_names) == 0:
        team_names.append("No team")
    return team_names


def get_team_workflows(current_team):
    cur.execute("SELECT workspace_name FROM workspace_to_team WHERE team_name = '{}'".format(current_team))
    workflow_names = cur.fetchall()
    workflow_names = [workflow_names[i][0] for i in range(len(workflow_names))]
    if len(workflow_names) == 0:
        workflow_names.append("No workspaces")
    return workflow_names


def fill_image_file_params(file_name, picture, x1_input, y1_input, x2_input, y2_input, class_input):
    cur.execute(
        "SELECT x1, y1, x2, y2, class, image_width, image_height FROM image_files WHERE file_name = '{}'".format(
            file_name))
    file_params = cur.fetchall()
    file_params = [file_params[0][i] for i in range(len(file_params[0]))]
    x1 = int(file_params[0])
    y1 = int(file_params[1])
    x2 = int(file_params[2])
    y2 = int(file_params[3])
    x1_input.setText(str(x1))
    y1_input.setText(str(y1))
    x2_input.setText(str(x2))
    y2_input.setText(str(y2))
    class_input.setText(str(file_params[4]))
    width = file_params[5]
    height = file_params[6]
    picture.resize(width, height)
    image_root = path_to_ui = Path(Path.cwd(), 'data', file_name)

    image = PIL.Image.open(image_root)
    draw = ImageDraw.Draw(image)
    draw.line(
        xy=(
            (x1, y1),
            (x1, y2),
            (x2, y2),
            (x2, y1),
            (x1, y1)
        ), fill='red', width=3)
    q_image = ImageQt(image).copy()
    pixmap = QPixmap.fromImage(q_image)
    picture.clear()
    picture.setPixmap(QPixmap.fromImage(q_image))
    picture.adjustSize()


def save_image_changes(file_name, x1_input, y1_input, x2_input, y2_input, class_input):
    x1 = x1_input.text()
    y1 = y1_input.text()
    x2 = x2_input.text()
    y2 = y2_input.text()
    class_text = class_input.text()
    cur.execute(
        "UPDATE image_files SET x1='{}', y1='{}', x2='{}', y2='{}', class='{}' WHERE file_name='{}'".format(x1, y1, x2,
                                                                                                            y2,
                                                                                                            class_text,
                                                                                                            file_name))
    con.commit()


def fill_members(table_obj, team_name):
    cur.execute("SELECT first_name, last_name,email FROM users WHERE id in (select user_id from team_to_user  where "
                "team_name = '{}');".format(team_name))
    members = cur.fetchall()
    if len(members) == 0:
        members.append(['No members', '', ''])
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
