from sqlalchemy import create_engine, Column, Integer, String, Interval, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.engine import Engine

from sqlite3 import Connection as SQLite3Connection


engine = create_engine('sqlite:///diligent.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

# class Tasks(Base):
#     __tablename__ = "tasks"
#     id = Column('id', Integer, primary_key=True)
#     task_name = Column('task_name', String)
#     priority_level = Column('priority_level', Integer)
#     length = Column('length', Integer)

# class PriorityQueue(Base):
#     __tablename__ = "priority_queue"
#     id = Column('id', Integer, primary_key = True)
#     task_id = Column(Integer, ForeignKey('tasks.id'))


# Base.metadata.create_all(bind=engine)
# Session = sessionmaker(bind=engine)

# session = Session()
# print (Base.metadata.tables.keys())
# session.close()