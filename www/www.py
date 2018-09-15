from flask import Flask, request, redirect,render_template,url_for
import logging
from sqlalchemy import  Column,String,Integer,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config_default


#1.两个数据库合二为一
#2. 增加模糊查询like
#3.自制线程池
#4.模板的优化


# 创建对象基类
Base = declarative_base()
class Book(Base):
    # 表的名字:
    __tablename__ = 'recommend'
    # 表的结构:
    bookid = Column(Integer, primary_key=True)
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

app = Flask(__name__)
@app.route('/',methods = ['GET'])
def index():
    #主页
    return render_template('index.html')

@app.route('/',methods = ['POST'])
def submit():
        title = request.form['bookname'].strip()
        if not title:
            return render_template('not_find.html', info='输入不能为空'), 404
        books = find_by_title(title)
        if not books:
            likes = find_with_like(title)
            if likes:
                #找到相似的
                return render_template('which_one.html', books=likes)
            else:
                #没找到
                return render_template('not_find.html',info = '你查询的《'+title+'》未收录'), 404
        elif len(books) == 1:
            #找到一本
            [book] = books
            return redirect(url_for('recommend',bookid = book.bookid))
        else:
            #找到好几本
            return render_template('which_one.html', books=books)


@app.route('/recommend/<int:bookid>', methods = ['GET'])
#可以用 <converter:variable_name> 指定一个可选的转换器。
def recommend(bookid):
    top = find_by_id(bookid) #得到[bookid,title,author,1,2,3,4,5,6,7,8]
    if top:
        A_tops = [getattr(top,'t'+str(i)) for i in range(1,9)] #id的集合
        B_tops = [getattr(top,'ut'+str(i)) for i in range(1,9)]
        A_tops_info = [find_by_id(t) for t in A_tops] #对象的集合
        B_tops_info = [find_by_id(t) for t in B_tops]
        return render_template('book.html', me = top,topA=A_tops_info,topB =B_tops_info)
    else:
        return render_template('not_find.html',info = '本书不存在')

#这里要修改,不能查询多个。
def find_by_title(title):
    session = DBSession()
    books = session.query(Book).filter(Book.title == title).all()
    session.close()
    return books

def find_with_like(title):
    session = DBSession()
    t = '%' + title + '%'
    books = session.query(Book).filter(Book.title.like(t)).all()
    session.close()
    return books

def find_by_id(bookid):
    session = DBSession()
    book = session.query(Book).filter(Book.bookid == bookid).one()
    session.close()
    return book



if __name__ == '__main__':
    configs = config_default.configs
    #启动logger
    logging.basicConfig(filename='myapp.log',level=logging.WARNING, filemode='a', \
                        format=configs['log']['format'], datefmt=configs['log']['datefmt'])
    logger = logging.getLogger(__name__)

    # 初始化数据库连接
    engine = create_engine(configs['db'], pool_recycle=7200)
    DBSession = sessionmaker(bind=engine)
    #启动服务器
    app.logger.info('Start the server!!!!!')
    app.run(host='0.0.0.0',port = 80) #port = 80,debug = True


#删除多余的logger,记录错误的logger(warning)


