from PyQt5.QtWidgets import QTableWidgetItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import BigInteger, Column, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import relationship
from pathlib import Path
import psycopg2
from random import randint

Base = declarative_base()
metadata = Base.metadata

con = psycopg2.connect(
    database="dataset_marker",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cur = con.cursor()


def connect():
    """connect function"""
    """con = psycopg2.connect(
        database="dataset_marker",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )"""
    path_to_config_file = Path(Path.cwd(), 'config.txt')
    with open(path_to_config_file, 'r', encoding='utf-8') as f:
        config = f.readline()
    return config


engine = create_engine("postgresql://postgres:@localhost/dataset_marker")


def register(email, password, first_name, phone_number, last_name, gender):
    cur.execute("INSERT INTO users VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(email, first_name, phone_number,
                                                                                       last_name, gender,
                                                                                       str(randint(100, 200)),
                                                                                       password))

    con.commit()


def user_authorisation(login, password):
    Session = sessionmaker(bind=engine)
    session = Session()
    authorisation_params = {'email': login, 'password': password}
    output_query = session.query(globals()['User']).filter_by(**authorisation_params)
    authorised = False
    cur.execute("SELECT id FROM users WHERE email = '{}'".format(login))
    user_id = cur.fetchall()
    for element in output_query:
        authorised = True
    return authorised, user_id[0][0]


def get_team_names(user_id):
    cur.execute("SELECT team_name FROM team WHERE user_id = '{}'".format(user_id))
    team_names = cur.fetchall()
    team_names = [team_names[i][0] for i in range(len(team_names))]
    return team_names


def get_team_workflows(current_team):
    cur.execute("SELECT workflow_name FROM workflows WHERE team_name = '{}'".format(current_team))
    workflow_names = cur.fetchall()
    workflow_names = [workflow_names[i][0] for i in range(len(workflow_names))]
    return workflow_names


def fill_members(table_obj, team_name):
    cur.execute("SELECT first_name, last_name,email FROM users WHERE id in (select user_id from team  where team_name "
                "= '{}');".format(team_name))
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
    table_obj.resizeColumnsToContents()


def fill_projects(table_obj, workspace_name):
    cur.execute("SELECT dataset_name, task_type, description FROM datasets_description WHERE dataset_name in (select "
                "dataset_name from dataset_to_workspace where workspace_name = '{}')".format(workspace_name))
    datasets = cur.fetchall()
    table_obj.setColumnCount(len(datasets[0]))
    table_obj.setHorizontalHeaderLabels(['Dataset name', 'Task type', 'Description'])
    table_obj.setRowCount(len(datasets))
    k = 0
    for row in datasets:
        for i in range(len(row)):
            table_obj.setItem(k, i, QTableWidgetItem(str(row[i])))
        k += 1
    table_obj.verticalHeader().setVisible(False)
    table_obj.resizeColumnsToContents()


def get_user_teams():
    pass


def change_team():
    pass


def fill_table(table_obj, table_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    form = session.query(globals()[table_name])
    attributes_names = []
    for name in globals()[table_name].__dict__.keys():
        if name[0] != '_':
            attributes_names.append(name)
    table_obj.setColumnCount(len(attributes_names))
    table_obj.setHorizontalHeaderLabels(attributes_names)
    table_obj.setRowCount(form.count())
    k = 0
    for row in form:
        for i in range(len(attributes_names)):
            table_obj.setItem(k, i, QTableWidgetItem(str(getattr(row, attributes_names[i]))))
        k += 1
    table_obj.resizeColumnsToContents()


class DatasetsDescription(Base):
    __tablename__ = 'datasets_description'

    dataset_name = Column(String, primary_key=True)
    task_type = Column(String, nullable=False)
    description = Column(Text)


class Workflow(DatasetsDescription):
    __tablename__ = 'workflow'

    workflow_name = Column(ForeignKey('datasets_description.dataset_name'), primary_key=True)
    dataset_name = Column(String)


class ImageDataset(Base):
    __tablename__ = 'image_datasets'

    file_name = Column(String, primary_key=True)
    x1 = Column(BigInteger, nullable=False)
    y1 = Column(BigInteger, nullable=False)
    x2 = Column(BigInteger, nullable=False)
    y2 = Column(BigInteger, nullable=False)
    _class = Column('class', String, nullable=False)
    image_width = Column(BigInteger, nullable=False)
    image_height = Column(BigInteger, nullable=False)
    image_represention = Column(LargeBinary, nullable=False)


class TextDataset(Base):
    __tablename__ = 'text_datasets'

    file_name = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    label = Column(String, nullable=False)
    text_fragment = Column(Text, nullable=False)


class User(Base):
    __tablename__ = 'users'

    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    id = Column(String, primary_key=True)
    password = Column(String, nullable=False)


class DatasetToFile(Base):
    __tablename__ = 'dataset_to_file'

    file_name = Column(String, primary_key=True)
    dataset_name = Column(ForeignKey('datasets_description.dataset_name'))

    datasets_description = relationship('DatasetsDescription')


class DatasetToUser(Base):
    __tablename__ = 'dataset_to_user'

    dataset_name = Column(ForeignKey('datasets_description.dataset_name'), primary_key=True, nullable=False)
    user_id = Column(String, primary_key=True, nullable=False)

    datasets_description = relationship('DatasetsDescription')
