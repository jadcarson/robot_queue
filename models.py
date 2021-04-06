from sqlalchemy import create_engine, Column, Integer, String, Interval, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from database import Base

class Tasks(Base):
    __tablename__ = "tasks"
    id = Column('id', Integer, primary_key=True)
    task_name = Column('task_name', String)
    priority_level = Column('priority_level', Integer)
    length = Column('length', Integer)

class PriorityQueue(Base):
    __tablename__ = "priority_queue"
    id = Column('id', Integer, primary_key = True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    robot_id=Column('robot_id', Integer)
    status = Column('status', String)
    task = relationship("Tasks", backref="queued")