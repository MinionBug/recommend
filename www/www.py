from flask import Flask, request, redirect,render_template,url_for
import logging
from sqlalchemy import  Column,String,create_engine
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
    bookid = Column(String(20), primary_key=True)
    title = Column(String(40))
    author = Column(String(40))
    top1 = Column(String(40))
    top2 = Column(String(40))
    top3 = Column(String(40))
    top4 = Column(String(40))
    top5 = Column(String(40))

app = Flask(__name__)
@app.route('/',methods = ['GET'])
def index():
    #主页
    return render_template('index.html')

@app.route('/',methods = ['POST'])
def submit():
        title = request.form['bookname'].strip()
        if title:
            return redirect(url_for('recommend', title=title))
        else:
            return render_template('not_find.html',info = '输入不能为空。'), 404


@app.route('/recommend/<title>', methods = ['GET'])
#可以用 <converter:variable_name> 指定一个可选的转换器。
def recommend(title):
    app.logger.info('用户查询:%s' % title)
    book = inquire_by_titles(title) #得到[bookid,title,author,1,2,3,4,5]
    if book:
        tops = [book.top1,book.top2,book.top3,book.top4,book.top5]
        tops_info = inquire_by_titles(tops)
        return render_template('book.html', tops=tops_info)
    else:
        app.logger.info('%s没找到' % title)
        maybe_books = inquire_with_like(title) #这是一个类的集合,需要传入的是书名
        maybe_titles = [maybe_book.title for maybe_book in maybe_books]
        return render_template('not_find.html',info = '你查询的《'+title+'》未收录',maybe_books=maybe_titles)

#这里要修改,不能查询多个。
def inquire_by_titles(titles):
    session = DBSession()
    result = []
    if isinstance(titles,list):
        for title in titles:
            book = session.query(Book).filter(Book.title == title).first()
            result.append(book)
        session.close()
        return result
    else:
        book = session.query(Book).filter(Book.title == titles).first()
        session.close()
        return book


def inquire_with_like(titles):
    session = DBSession()
    result = []
    if isinstance(titles,list):
        for title in titles:
            t = '%' + title + '%'
            book = session.query(Book).filter(Book.title.like(t)).all()
            result.append(book)
        session.close()
        return result
    else:
        t = '%'+titles+'%'
        book = session.query(Book).filter(Book.title.like(t)).all()
        session.close()
        return book


if __name__ == '__main__':
    configs = config_default.configs
    #启动logger
    logging.basicConfig(filename='myapp.log',level=logging.INFO, filemode='a', \
                        format=configs['log']['format'], datefmt=configs['log']['datefmt'])
    logger = logging.getLogger(__name__)

    # 初始化数据库连接
    engine = create_engine(configs['db'], pool_recycle=7200)
    DBSession = sessionmaker(bind=engine)
    #启动服务器
    app.logger.info('Start the server!!!!!')
    app.run(host='0.0.0.0',port = 80) #port = 80,debug = True





