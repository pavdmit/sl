import psycopg2
import random
from random import randint
import string
from PIL import Image
import io
import pandas as pd

con = psycopg2.connect(
    database="dataset_marker",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)


def copy_func():
    cur = con.cursor()
    cur.execute("SELECT email FROM users")
    emails = cur.fetchall()
    cur.execute("SELECT first_name FROM users")
    first_names = cur.fetchall()
    cur.execute("SELECT phone_number FROM users")
    phone_numbers = cur.fetchall()
    cur.execute("SELECT last_name FROM users")
    last_names = cur.fetchall()
    cur.execute("SELECT gender FROM users")
    genders = cur.fetchall()
    cur.execute("SELECT id FROM users")
    ids = cur.fetchall()
    characters = string.ascii_letters + string.digits
    passwords = [''.join(random.choice(characters) for i in range(6)) for j in range(100)]
    for i in range(len(ids)):
        cur.execute(
            "INSERT INTO users2 VALUES ( '{}', '{}', '{}','{}', '{}', '{}','{}' )".format(
                emails[i][0], first_names[i][0], phone_numbers[i][0], last_names[i][0],
                genders[i][0], ids[i][0], passwords[i]))
        con.commit()


def image_datasets_generator():
    cur = con.cursor()
    # dandelions
    for i in range(1, 21):
        image_class = "dandelion"
        filename = "dandelion" + str(i) + ".jpg"
        with Image.open(filename) as image:
            width, height = image.size
        """im = Image.open('dandelion1.jpg')
        binary_repr = io.BytesIO()
        im.save(binary_repr, format='JPEG')"""
        binary_repr = open(filename, 'rb').read()
        cur.execute(
            "INSERT INTO image_datasets VALUES ( '{}', '{}', '{}','{}', '{}', '{}','{}','{}',{} )".format(
                filename, randint(0, 100), randint(0, 100), randint(0, 100),
                randint(0, 100), image_class, width, height, psycopg2.Binary(binary_repr)))
        con.commit()

    # roses
    for i in range(1, 21):
        image_class = "rose"
        filename = "rose" + str(i) + ".jpg"
        with Image.open(filename) as image:
            width, height = image.size
        binary_repr = open(filename, 'rb').read()
        cur.execute(
            "INSERT INTO image_datasets VALUES ( '{}', '{}', '{}','{}', '{}', '{}','{}','{}',{} )".format(
                filename, randint(0, 100), randint(0, 100), randint(0, 100),
                randint(0, 100), image_class, width, height, psycopg2.Binary(binary_repr)))
        con.commit()

    # sunflowers
    for i in range(1, 21):
        image_class = "sunflower"
        filename = "sunflower" + str(i) + ".jpg"
        with Image.open(filename) as image:
            width, height = image.size
        binary_repr = open(filename, 'rb').read()
        cur.execute(
            "INSERT INTO image_datasets VALUES ( '{}', '{}', '{}','{}', '{}', '{}','{}','{}',{} )".format(
                filename, randint(0, 100), randint(0, 100), randint(0, 100),
                randint(0, 100), image_class, width, height, psycopg2.Binary(binary_repr)))
        con.commit()

    # tulips
    for i in range(1, 21):
        image_class = "tulip"
        filename = "tulip" + str(i) + ".jpg"
        with Image.open(filename) as image:
            width, height = image.size
        binary_repr = open(filename, 'rb').read()
        cur.execute(
            "INSERT INTO image_datasets VALUES ( '{}', '{}', '{}','{}', '{}', '{}','{}','{}',{} )".format(
                filename, randint(0, 100), randint(0, 100), randint(0, 100),
                randint(0, 100), image_class, width, height, psycopg2.Binary(binary_repr)))
        con.commit()


def dataset_to_file_generator():
    cur = con.cursor()
    cur.execute("SELECT file_name FROM image_datasets")
    file_names = cur.fetchall()
    dataset_names = ['flowers']
    for i in range(len(file_names)):
        cur.execute(
            "INSERT INTO dataset_to_file VALUES ( '{}', '{}' )".format(file_names[i][0], dataset_names[0]))
    con.commit()


def dataset_to_user():
    cur = con.cursor()
    cur.execute("SELECT id FROM users")
    users_id = cur.fetchall()
    cur.execute("SELECT dataset_name FROM datasets_description")
    datasets_names = cur.fetchall()
    print(users_id)
    print(datasets_names)
    for i in range(101):
        cur.execute(
            "INSERT INTO dataset_to_user VALUES ( '{}', '{}' )".format(
                datasets_names[randint(0, len(datasets_names) - 1)][0], users_id[randint(0, len(users_id) - 1)][0]))
        con.commit()


def text_datasets():
    data = pd.read_csv('lenta_valid.csv', nrows=100)
    cur = con.cursor()
    print(data.head())
    print(data.columns)
    count = 1
    for i, row in data.iterrows():
        filename = 'text' + str(count)
        # print(i,row[0],row[1],row[2],row[3])
        cur.execute(
            "INSERT INTO text_datasets VALUES ( '{}', '{}','{}','{}' )".format(
                filename, row[1], row[4],row[2] ))
        count = count+1
        con.commit()


def workflow():
    cur = con.cursor()
    cur.execute("SELECT dataset_name FROM datasets_description")
    datasets_names = cur.fetchall()
    for i in range(20):
        workflow_name = 'workflow' + str(randint(0,10))
        cur.execute(
            "INSERT INTO workflow VALUES ( '{}', '{}' )".format(
                workflow_name, datasets_names[randint(0, len(datasets_names)-1 )][0]))
        con.commit()

# copy_func()
# image_datasets_generator()
# dataset_to_file_generator()
# dataset_to_user()
# text_datasets()
workflow()
