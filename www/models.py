from sqlalchemy import  Column,String,Integer,create_engine,DateTime,Text,Float,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,backref
import time,uuid

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

#1.一个问题,是否需要减少交叉查询?
Base = declarative_base()
class Book(Base): #要增加更多关于来源等信息
    # 表的名字:
    __tablename__ = 'book'
    # 表的结构:
    bid = Column(Integer, primary_key=True)
    title = Column(String(40))
    author = Column(String(40))
    words = Column(Integer)
    finished = Column(String(40))
    link = Column(String(60))


class User(Base):
    __tablename__ = 'user'
    uid = Column(Integer,primary_key=True)
    email = Column(String(50))
    passwd = Column(String(50))
    name = Column(String(50))
    created_at = Column(Float(16,6),default = time.time)  #这里应该是时间

class UserBook(Base):
    __tablename__ = 'userbook'
    cid = Column(Integer,primary_key=True)
    uid = Column(Integer)
    bid = Column(Integer)
    readed = Column(Integer)
    star = Column(Integer)
    comment = Column(Text)
    created_at = Column(Float(16,6))


class Tag(Base):
    __tablename__ = 'tag'
    tid = Column(Integer,primary_key=True)
    bid = Column(Integer)
    uid = Column(Integer)
    tag = Column (String(30)) #汉字乘以3,10个汉字以内
    created_at = Column(Float(16,6),default = time.time)  # 这里应该是时间
    weight = Column(Integer)

class BookRecommend(Base):
    __tablename__ = 'bookrecommend'
    bid = Column(Integer,primary_key=True)
    title = Column(String(40))
    author = Column(String(40))
    t1 = Column(Integer)
    t2 = Column(Integer)
    t3 = Column(Integer)
    t4 = Column(Integer)
    t5 = Column(Integer)
    t6 = Column(Integer)
    t7 = Column(Integer)
    t8 = Column(Integer)
    ut1 = Column(Integer)
    ut2 = Column(Integer)
    ut3 = Column(Integer)
    ut4 = Column(Integer)
    ut5 = Column(Integer)
    ut6 = Column(Integer)
    ut7 = Column(Integer)
    ut8 = Column(Integer)


class UserRecommend(Base):
    __tablename__ = 'userrecommend'
    uid = Column(Integer,primary_key=True)
    t1 = Column(Integer)
    t2 = Column(Integer)
    t3 = Column(Integer)
    t4 = Column(Integer)
    t5 = Column(Integer)
    t6 = Column(Integer)
    t7 = Column(Integer)
    t8 = Column(Integer)



