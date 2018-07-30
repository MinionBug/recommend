from flask import Flask, request, redirect,render_template,url_for
import logging
from sqlalchemy import  Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config_default

#每次本地环境销毁的时候,断开数据库。


def salt(bookid):
    return str(int(bookid)*2+15)

def un_salt(bookid):
    return int((int(bookid)-15)/2)

# 创建对象基类
Base = declarative_base()
class Book(Base):
    # 表的名字:
    __tablename__ = 'books'
    # 表的结构:
    id = Column(String(20), primary_key=True)
    title = Column(String(40))
    author = Column(String(40))

class TopRelate(Base):
    __tablename__ = 'toprelate'
    bookid = Column(String(20), primary_key=True)
    top1 = Column(String(20))
    top2 = Column(String(20))
    top3 = Column(String(20))
    top4 = Column(String(20))
    top5 = Column(String(20))


app = Flask(__name__)
@app.route('/',methods = ['GET'])
def index():
    #主页
    return render_template('index.html')

@app.route('/',methods = ['POST'])
def submit():
        bookname = request.form['bookname'].strip()
        if bookname:
            app.logger.info('用户查询 %s' % bookname)
            session = DBSession()
            inquiry_book = session.query(Book).filter(Book.title == bookname).first()
            session.commit()
            if inquiry_book:
                bookid = inquiry_book.id
                salt_bookid = salt(bookid)  # 这里对bookid进行加密
                return redirect(url_for('recommend', salt_bookid=salt_bookid))
            else:
                app.logger.info('从数据库没找到 %s' % bookname)
                return render_template('not_find.html',info = '本书未收录。'), 404
        else:
            return render_template('not_find.html',info = '输入不能为空。'), 404


@app.route('/recommend/<int:salt_bookid>', methods = ['GET'])
#可以用 <converter:variable_name> 指定一个可选的转换器。
def recommend(salt_bookid):
    bookid = un_salt(salt_bookid)
    app.logger.info('查询 %s' % bookid)
    session = DBSession()
    top_info = session.query(TopRelate).filter(TopRelate.bookid == bookid).first()
    session.commit()
    if top_info:
        app.logger.info('找到推荐')
        top_ids = [top_info.top1,top_info.top2,top_info.top3,top_info.top4,top_info.top5]
        #将各个书的各个属性,加入列表当中
        topbooks = []
        for top_id in top_ids:
            t = session.query(Book).filter(Book.id == top_id).first()
            session.commit()
            topbooks.append([salt(t.id),t.title,t.author])
        return render_template('book.html', tops=topbooks)
    else:
        app.logger.info('未找到推荐')
        return render_template('not_find.html',info = '本书未收录')


if __name__ == '__main__':
    configs = config_default.configs
    #启动logger
    logging.basicConfig(filename='myapp.log',level=logging.INFO, filemode='a', \
                        format=configs['log']['format'], datefmt=configs['log']['datefmt'])
    logger = logging.getLogger(__name__)

    # 初始化数据库连接
    engine = create_engine(configs['db'], pool_recycle=3600)
    DBSession = sessionmaker(bind=engine)
    #启动服务器
    app.logger.info('Start the server!!!!!')
    app.run(host='0.0.0.0',port = 80) #port = 80,debug = True





