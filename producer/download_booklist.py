import requests
from bs4 import BeautifulSoup
import asyncio,aiohttp
import random,time
import json
import mysql.connector

#添加logging功能
#问题:1. 代理不管用。2. 出现错误的代理,怎么把它放置,可能是要搞个先进先出。
headers = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'IE 9.0User-Agent:Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER) ',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36']
tasks = []
maxSem = 5
proxies = {}
rbookurl = 'http://www.yousuu.com/book/'
#####协程
###多代理

def RandomUserAgent():
    header = {'User-Agent': random.choice(headers)}
    return header

def loadProxy():
    try:
        with open('/Users/Fish/PycharmProjects/Programming Project/ProxyPool/proxy.json') as f:
            global proxies
            proxies = json.load(f)
            print ('load proxy:',proxies)
    except Exception as e:
        print ('load proxy:',e)

def RandomProxy():
    ip=random.choice(list(proxies.keys()))
    port = proxies[ip]
    print ('http://%s:%s' %(ip,port))
    return 'http://%s:%s' %(ip,port)

def get_book(i,j):
    for i in range(i,j):#150000
        try:
            bookurl = rbookurl + str(i)
            r = requests.get(bookurl, headers=RandomUserAgent(),timeout = 3)  # proxy=RandomProxy()代理有的行,有的不行。
            soup = BeautifulSoup(r.text, 'html.parser')
            all = soup.find('div', class_='col-sm-7')
            title = all.find('span', style="font-size:18px;font-weight:bold;").text
            li = all.find_all('li')
            for n in range(len(li)):
                li[n] = li[n].text
            author = li[0][3:]
            word_count = li[1][3:-2]
            updated = li[4][5:-6]
            cursor.execute('insert into books (id,title,author,word_count,updated) values (%s,%s,%s,%s,%s)',
                           [i, title, author, word_count, updated])
            print('insert:', i)
        except Exception as e:
            print (e)


#loadProxy()
########
def book_main():
    for i in range(11,50):
        conn = mysql.connector.connect(user='root', password='password', database='Recommend')
        cursor = conn.cursor()
        #cursor.execute('create table books(id varchar(20) primary key, title varchar(40),author varchar(40),word_count varchar(20),updated varchar(40))')
        get_book(i*1000,(i+1)*1000)
    #    get_book(i*1000,(i+1)*1000)
        ######
        #cursor.execute('select * from books where id = %s', ('1',))
        #cursor.fetchall()
        #print(cursor.rowcount)
        conn.commit()
        cursor.close()



def get_urllist(): #http://www.yousuu.com/booklist/57219239b33f5bc64078bac3
    urllist = 'http://www.yousuu.com/booklist?'
    i = 1
    # 连接数据库
    while True:
        try:
            print ('--------------------1.urllist:', urllist, '--------------------',i)
            r = requests.get(urllist, headers=RandomUserAgent(),timeout = 3)
            soup = BeautifulSoup(r.text, 'html.parser')
            ## #############获得下一个########################必须要先,否则出现错误就一直循环了
            ul = soup.find('ul', class_='pagination')
            a = ul.find_all('a')[1]
            urllist = 'http://www.yousuu.com/booklist?t=' + a.get('onclick')[23:-2]
            i+=1
            #####获得书单网址#######
            trs = soup.find_all('tr', class_='list-item')
            for tr in trs:
                href = tr.find('h4').find('a').get('href')
                booknum = int(tr.find_all('td')[3].get_text()[:-2])
                print('2. url:',href,', booknum:',booknum)
                get_booklist(href,booknum)
            #提交数据库
            #conn.commit()
        except Exception as e:
            print (e)
            pass



def get_booklist(href,n):
    url = 'http://www.yousuu.com'+href
    r = requests.get(url, headers=RandomUserAgent(),timeout = 3)
    soup = BeautifulSoup(r.text, 'html.parser')
    for div in soup.find_all('div', class_='bd booklist-subject'):
        bookid = div.find('div',class_ = 'title').find('a').get('href')[6:]
        raw_star= div.find('span',class_ = 'num2star').string
        if raw_star:
            star = int(raw_star)
        else:
            star = 0#如果没有star,就是0
        cursor.execute('insert into booklist(id,bookid,star) values (%s,%s,%s)', [href[10:], bookid, star])
        # cursor.execute('insert into booklist(id,bookid,star) values (%s,%s,%s)',['5a9d19a57284101a147cb6b6', '12345', 3])
        # print ('3',href[10:],'id:',bookid,star)
    if n > 50:
        for i in range(1, n // 50 + 1):  # (75的情况下,range(1,2),i = 1)
            func(href, i + 1)
    conn.commit()


def func(href,i):
    url = 'http://www.yousuu.com'+href +'?page='+str(i)
    r = requests.get(url, headers=RandomUserAgent(),timeout = 3)
    soup = BeautifulSoup(r.text, 'html.parser')
    for div in soup.find_all('div',class_ ='bd booklist-subject'):
        bookid = div.find('div',class_ = 'title').find('a').get('href')[6:]
        raw_star= div.find('span',class_ = 'num2star').string
        if raw_star:
            star = int(raw_star)
        else:
            star = 0#如果没有star,就是0
        cursor.execute('insert into booklist(id,bookid,star) values (%s,%s,%s)',[href[10:],bookid,star])
        #print('3', href[10:], 'id:', bookid, star)


conn = mysql.connector.connect(user='root', password='password', database='Recommend')
cursor = conn.cursor()
get_urllist()
cursor.close()

