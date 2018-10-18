from flask import Flask, request, redirect,render_template,url_for,make_response,session,flash
import logging
from sqlalchemy import  Column,String,Integer,create_engine,DateTime,Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config_default
import hashlib
from models import Book,User,UserBook,Tag,BookRecommend,UserRecommend
from datetime import datetime
import time


_COOKIE_KEY = 'whatever'

app = Flask(__name__)
app.secret_key =config_default.configs['secret_key']


@app.route('/',methods = ['GET','POST'])
def index():
    #主页
    if request.method =='POST':
        title = request.form['bookname'].strip()
        if not title:
            return render_template('not_find.html', info='输入不能为空'), 404
        s = DBSession()
        books = s.query(Book).filter(Book.title == title).all()
        if len(books) == 1:
            #找到一本
            [book] = books
            s.close()
            return redirect(url_for('book',bookid = book.bid))
        elif len(books)>1:
            s.close()
            return render_template('which_one.html', books=books)
        else:
            t = '%' + title + '%'
            likes = s.query(Book).filter(Book.title.like(t)).all()
            s.close()
            if likes:
                #找到相似的
                return render_template('which_one.html', books=likes)
            else:
                #没找到
                return render_template('not_find.html',info = '你查询的《'+title+'》未收录')
    else:
        user = check_login(session)
        log_name = user.name if user else None
        return render_template('index.html',log_name = log_name)

@app.route('/book/<int:bookid>')
def book(bookid):
    user = check_login(session)
    # 打开书页
    s = DBSession()
    # 先确认一次是否有这本书
    log_name = user.name if user else None
    book = s.query(Book).filter(Book.bid == bookid).first()
    if book:
        recommend = s.query(BookRecommend).filter(BookRecommend.bid == bookid).first()
        tops_id = [getattr(recommend, 't' + str(i)) for i in range(1, 9)]  # id的集合
        utops_id = [getattr(recommend, 'ut' + str(i)) for i in range(1, 9)]
        tops = [s.query(Book).filter(Book.bid == t).first() for t in tops_id]  # 对象的集合
        utops = [s.query(Book).filter(Book.bid == t1).first() for t1 in utops_id]
        comments = s.query(UserBook).filter(UserBook.bid == bookid).all()
        t = s.query(Tag).filter(Tag.bid == bookid).all()
        tags_with_count = handle_tag(t)
        s.close()
        return render_template('book.html', book=book, tops=tops, utops=utops, comments=comments, tags=tags_with_count,
                               log_name=log_name)
    else:
        return render_template('not_find.html', info='本书不存在')

def handle_tag(tags):
    #tag要经过处理,计算多少种,数量有多少,以便按照大小排列
    t = dict()
    for tag in tags:
        tt = tag.tag
        if tt not in t:
            t[tt] = 1
        else:
            t[tt]+=1
    return t

@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        passwd1 = request.form['password1'].strip()
        passwd2 = request.form['password2'].strip()
        if not name or not email or not passwd1 or not passwd2:
            return render_template('register.html',error = '必填项不能为空')
        if passwd1 != passwd2:
            return render_template('register.html',error = '两次密码输入不相同')
        s = DBSession()
        users = s.query(User).filter(User.email == email).all()
        if len(users) > 0:
            s.close()
            return render_template('register.html',error = '邮箱已存在')
        passwd = '%s:%s' % (email, passwd1)
        sha_passwd = hashlib.sha1(passwd.encode('utf-8')) #.encode('utf-8')
        user = User(name= name,email=email,passwd = sha_passwd.hexdigest()) #实例化
        #设置seesion,返回某个网页
        s.add(user)
        s.commit()
        session['uid'] = user.uid #这里不能在commit之前,否则是None
        s.close()
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        passwd = request.form['password'].strip()
        if not email:
            return render_template('login.html',error = '邮箱不能为空') #flash要在html里面有。
        if not passwd:
            return render_template('login.html',error = '密码不能为空')
        s = DBSession()
        users = s.query(User).filter(User.email == email).all()
        if len(users) == 0:
            return render_template('login.html',error = '邮箱不存在')
        user = users[0]
        #check passwd
        passwd = '%s:%s' % (email, passwd)
        sha1 = hashlib.sha1(passwd.encode('utf-8')) #.encode('utf-8')
        if user.passwd != sha1.hexdigest():
            return render_template('login.html',error = '邮箱或密码不准确') #error是什么还没研究好
        #set session
        session['uid'] = user.uid #这里和数据库的session冲突
        s.close()
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    if session and session.get('uid'):
    # remove the username from the session if it's there
        session.pop('uid', None)
    return redirect(url_for('index'))

@app.route('/usercenter')
def usercenter():
    user = check_login(session)
    if not user:
        return redirect(url_for('login'))
    else:
        s = DBSession()
        userbook = s.query(UserBook).filter(UserBook.uid == user.uid).all()
        urecommend = s.query(UserRecommend).filter(UserRecommend.uid == user.uid).first()
        utops = []
        if urecommend:
            utops_id = [getattr(urecommend, 't' + str(i)) for i in range(1, 9)]  # id的集合
            utops = [s.query(Book).filter(Book.bid == t).first() for t in utops_id]  # 对象的集合
        s.close()
        return render_template('usercenter.html',user = user,userbook = userbook,utops = utops)

#@app.route('/user/<int:userid>')
#def user():
#    pass


def check_login(session):
    if not session or not session.get('uid'):
        return None
    uid = session['uid']
    s = DBSession()
    u = s.query(User).filter(User.uid == uid).all()
    s.close()
    if u:
        user = u[0]
        return user
    else:
        return None

@app.route('/book/feedback_readed/<int:bookid>/', methods=['POST'])
def feedback_readed(bookid):
    #添加tag
    user = check_login(session)
    if not user:
        return redirect(url_for('index'))
    uid = session['uid']
    readed = request.form['readed']
    try:
        s = DBSession()
        exist = s.query(UserBook).filter(uid = uid,bid = bookid).first()
        if not exist:
            new = UserBook(uid = uid,bid = bookid,readed = readed)
            s.add(new)
        else:
            exist.readed = readed
        s.commit()
        s.close()
    except Exception as e:
        app.logger.warning(e)

@app.route('/book/feedback_star/<int:bookid>/', methods=['POST'])
def feedback_star(bookid):
    #添加tag
    user = check_login(session)
    if not user:
        return redirect(url_for('index'))
    uid = session['uid']
    star = request.form['star']
    try:
        s = DBSession()
        exist = s.query(UserBook).filter(uid = uid,bid = bookid).first()
        if not exist:
            new = UserBook(uid = uid,bid = bookid,star = star)
            s.add(new)
        else:
            exist.star = star
        s.commit()
        s.close()
    except Exception as e:
        app.logger.warning(e)

@app.route('/book/feedback_comment/<int:bookid>/', methods=['POST'])
def feedback_comment(bookid):
    #添加tag
    user = check_login(session)
    if not user:
        return redirect(url_for('index'))
    uid = session['uid']
    comment = request.form['comment']
    try:
        s = DBSession()
        exist = s.query(UserBook).filter(uid = uid,bid = bookid).first()
        if not exist:
            new = UserBook(uid = uid,bid = bookid,comment = comment)
            s.add(new)
        else:
            exist.comment = comment
        s.commit()
        s.close()
    except Exception as e:
        app.logger.warning(e)

@app.route('/book/feedback_tag/<int:bookid>/', methods=['POST'])
def feedback_tag(bookid):
    #添加tag
    user = check_login(session)
    if not user:
        return redirect(url_for('index'))
    uid = session['uid']
    tag_info = request.form['status'].strip()
    tags = tag_info.split('#')
    try:
        s = DBSession()
        #添加tag
        for tag in tags:
            t = Tag(uid=uid, bid=bookid, tag=tag)
            s.add(t)
        s.commit()
        s.close()
    except Exception as e:
        app.logger.warning(e)


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


