from flask import Flask, request, redirect,render_template,url_for,make_response,session,flash
import logging
from sqlalchemy import create_engine,and_
from sqlalchemy.orm import sessionmaker
import config_default
import hashlib
from models import *
import time
from flask import jsonify
import json
from flask_cors import CORS


#_COOKIE_KEY = 'whatever'

app = Flask(__name__)
app.secret_key =config_default.configs['secret_key']
CORS(app, resources=r'/*',supports_credentials = True)


@app.route('/search',methods = ['POST'])
def search():
    data = json.loads(request.get_data().decode("utf-8"))
    title = data['title']
    if not title:
        return jsonify({'error':'输入为空'})
    s = DBSession()
    t = '%' + title + '%'
    books = s.query(Book).filter(Book.title.like(t)).all()
    if books:
        books = [{'bid':book.bid,'title':book.title,'author':book.author} for book in books]
        return jsonify({'books':books})
    else:
        return jsonify({'error':'本书暂未收录'})


@app.route('/book/<int:bookid>')
def book(bookid):
    s = DBSession()
    ###
    book = s.query(Book).filter(Book.bid == bookid).first()
    if not book:
        return jsonify({'error':'本书不存在'})
    book_info = {'bid':bookid,'title':book.title,'author':book.author,'words':book.words,'finished':book.finished,'link':book.link}
    #recommend
    recommend = s.query(BookRecommend).filter(BookRecommend.bid == bookid).first()
    tops_id = [getattr(recommend, 't' + str(i)) for i in range(1, 9)]  # id的集合
    utops_id = [getattr(recommend, 'ut' + str(i)) for i in range(1, 9)]
    tops = [s.query(Book).filter(Book.bid == t).first() for t in tops_id]  # 对象的集合
    utops = [s.query(Book).filter(Book.bid == t1).first() for t1 in utops_id]
    tops_info = []
    utops_info = []
    for top in tops:
        tops_info.append({'bid':top.bid,'title':top.title,'author':top.author})
    for utop in utops:
        utops_info.append({'bid':utop.bid,'title':utop.title,'author':utop.author})
    #comment
    comment_info =[]
    comments = s.query(UserBook).filter(and_(UserBook.bid == bookid,UserBook.comment !=None)).all()
    for c in comments:
        #这里created_at如果是decimal的话,json居然无法
        user = s.query(User).filter(User.uid == c.uid).first()
        comment_info.append({'uid':c.uid,'name':user.name,'comment':c.comment,'created_at':float(c.created_at)})
    #tag
    t = s.query(Tag).filter(Tag.bid == bookid).all()
    tag_info = handle_tag(t)
    #查询自己输入的
    uid = check_login(session)
    feedback_info= {}
    if uid:
        ub = s.query(UserBook).filter(UserBook.bid == bookid, UserBook.uid == uid).first()
        if ub:
            feedback_info['readed'] = ub.readed
            feedback_info['star'] = ub.star
            #这里暂时存疑
            feedback_info['comment'] = ub.comment
    s.close()
    return jsonify({'bookinfo': book_info, 'comments': comment_info, 'tags': tag_info, 'tops': tops_info, 'utops': utops_info,'userbook':feedback_info})

def handle_tag(tags):
    #tag要经过处理,计算多少种,数量有多少,以便按照大小排列
    t ={}
    t_info = []
    for tag in tags:
        if tag.tag in t:
            t[tag.tag] += tag.weight
        else:
            t[tag.tag] = tag.weight
    for key,value in t.items():
        t_info.append({'tag':key,'weight':value})
    return t_info

@app.route('/register',methods = ['POST'])
def register():
    data = json.loads(request.get_data().decode("utf-8"))
    name = data['name'].strip()
    email = data['email'].strip()
    passwd1 = data['password1'].strip()
    passwd2 = data['password2'].strip()
    #简单验证
    if not name or not email or not passwd1 or not passwd2:
        return jsonify({'error':'输入为空'})
    if passwd1 != passwd2:
        return jsonify({'error':'两次密码输入不一致'})
    #开始
    s = DBSession()
    users = s.query(User).filter(User.email == email).all()
    if len(users) > 0:
        s.close()
        return jsonify({'error':'邮箱已存在'})
    passwd = '%s:%s' % (email, passwd1)
    sha_passwd = hashlib.sha1(passwd.encode('utf-8'))  # .encode('utf-8')
    user = User(name=name, email=email, passwd=sha_passwd.hexdigest(),created_at=float(time.time()))
    s.add(user)
    s.commit()
    session['uid'] = user.uid
    s.close()
    return jsonify({'uid':user.uid,'name':name})

@app.route('/login',methods = ['POST'])
def login():
    data = json.loads(request.get_data().decode("utf-8"))
    email = data.get('email')
    passwd = data.get('password')
    if not (email and email.strip()):
        return jsonify({'error':'邮箱为空'})
    if not passwd or not passwd.strip():
        return jsonify({'error':'密码为空'})
    s = DBSession()
    users = s.query(User).filter(User.email == email).all()
    if not users:
        s.close()
        return jsonify({'error':'邮箱不存在'})
    user = users[0]
    # check passwd
    passwd = '%s:%s' % (email, passwd)
    sha1 = hashlib.sha1(passwd.encode('utf-8'))  # .encode('utf-8')
    if user.passwd != sha1.hexdigest():
        s.close()
        return jsonify({'error':'邮箱或密码不正确'})  # error是什么还没研究好
    # set session
    session['uid'] = user.uid
    s.close()
    return jsonify({'uid':user.uid,'name':user.name})

@app.route('/logout')
def logout():
    if session and session.get('uid'):
    # remove the username from the session if it's there
        session.pop('uid')
        return jsonify({'OK': True})
    else:
        return jsonify({'error':'未登录'})


@app.route('/usercenter')
def usercenter():
    uid = check_login(session)
    if not uid:
        return jsonify({'error':'未登录'})
    s = DBSession()
    user = s.query(User).filter(User.uid ==uid).first()
    user_info = {'email':user.email}
    #ub
    userbooks = s.query(UserBook).filter(UserBook.uid == uid).all()
    ub_infos = []
    for ub in userbooks:
        book = s.query(Book).filter(Book.bid == ub.bid).first()
        ub_info = {'title':book.title,'author':book.author,'readed':ub.readed,'star':ub.star,'comment':ub.comment}
        ub_infos.append(ub_info)
    #recommend
    urecommend = s.query(UserRecommend).filter(UserRecommend.uid == uid).first()
    utops = []
    if urecommend:
        utops_id = [getattr(urecommend, 't' + str(i)) for i in range(1, 9)]  # id的集合
        utops = [s.query(Book).filter(Book.bid == t).first() for t in utops_id]  # 对象的集合
    s.close()
    return jsonify({'user_infos':user_info,'ub_info':ub_infos,'utops':utops})

#@app.route('/user/<int:userid>')
#def user():
#    pa

@app.route('/book/<int:bookid>/feedback/<arg>', methods=['POST'])
def feedback(bookid,arg):
    if arg not in ['readed','star','comment']:
        return {'error':'feedback中部包含此键'}
    uid = check_login(session)
    if not uid:
        return jsonify({'error':'未登录'})
    data = json.loads(request.get_data().decode("utf-8"))
    arg_value = data.get(str(arg))
    print (arg,arg_value)
    try:
        s = DBSession()
        book = s.query(Book).filter(Book.bid == bookid).all()
        if not book: #可以删掉,有try
            return jsonify({'error': '本书不存在'})
        exist = s.query(UserBook).filter(UserBook.uid == uid,UserBook.bid == bookid).first()
        if not exist:
            if str(arg) == 'comment':
                exist = UserBook(uid = uid,bid = bookid,arg = arg_value,created_at =float(time.time())) #如果是comment的话
            else:
                exist = UserBook(uid = uid,bid = bookid,arg = arg_value) #如果是comment的话
            s.add(exist)
        else:
            setattr(exist,arg,arg_value)
        s.commit()
        arg_info = {'uid': exist.uid, 'created_at': float(time.time()), str(arg): getattr(exist,arg)}
        s.close()
        return jsonify(arg_info)
    except Exception as e:
        app.logger.warning(e)
        return jsonify({'error': str(e)})


@app.route('/book/<int:bookid>/feedback/tag', methods=['POST'])
def feedback_tag(bookid):
    #添加tag
    uid = check_login(session)
    if not uid:
        return jsonify({'error':'未登录'})
    data = json.loads(request.get_data().decode("utf-8"))
    tag_data =data.get('tag')
    tags = tag_data.split('#')
    try:
        s = DBSession()
        book = s.query(Book).filter(Book.bid == bookid).all()
        if not book: #可以删掉,有try
            return jsonify({'error': '本书不存在'})
        #添加tag
        ts_info = []
        for tag in tags:
            if tag:
                exist = s.query(Tag).filter(Tag.bid == bookid,Tag.tag == tag).first()
                if exist:
                    exist.weight +=100
                else:
                    exist = Tag(uid=uid, bid=bookid, tag=tag,weight = 100)
                    s.add(exist)
                s.commit()
                t = {'uid': exist.uid, 'created_at': float(exist.created_at), 'tag': exist.tag,
                     'weight': exist[0].weight}
                ts_info.append(t)
        s.close()
        return jsonify({'tag':ts_info})
    except Exception as e:
        app.logger.warning(e)
        return jsonify({'error': str(e)})


def check_login(session):
    if not session or not session.get('uid'):
        return None
    uid = session['uid']
    s = DBSession()
    u = s.query(User).filter(User.uid == uid).all()
    s.close()
    if u:
        return uid
    else:
        return None
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
    app.run(host='0.0.0.0') #port = 80,debug = True




