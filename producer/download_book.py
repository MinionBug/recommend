import requests
from bs4 import BeautifulSoup
import asyncio,aiohttp
import random
import json
import mysql.connector

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


async def get_book(i,sem):
    with (await sem):
        try:
            bookurl = rbookurl + str(i)
            print (bookurl)
            async with aiohttp.ClientSession() as session:
                async with session.request('get', bookurl, headers=RandomUserAgent(), timeout = 5,\
                                           verify_ssl=False) as resp:#proxy=RandomProxy()代理有的行,有的不行。
                    r = await resp.text()
                    soup = BeautifulSoup(r, 'html.parser')
                    all = soup.find('div', class_='col-sm-7')
                    title = all.find('span', style="font-size:18px;font-weight:bold;").text
                    li = all.find_all('li')
                    for n in range(len(li)):
                        li[n]=li[n].text
                    author = li[0][3:]
                    word_count = li[1][3:-2]
                    updated = li[4][5:-6]
                    cursor.execute('insert into books (id,title,author,word_count,updated) values (%s,%s,%s,%s,%s)',[i,title,author,word_count,updated])
                    print('insert:',i, title, author, word_count, updated)
        except Exception as e:
            print('connect error', e)

#async def save_book(info):

loadProxy()
#######
conn = mysql.connector.connect(user='root', password='password', database='Recommend')
cursor = conn.cursor()
#cursor.execute('create table books(id varchar(20) primary key, title varchar(40),author varchar(40),word_count varchar(20),updated varchar(40))')
sem = asyncio.Semaphore(maxSem)  # 最大同步数量
for i in range(1,5):#14000
    tasks.append(get_book(i, sem))
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
######
#cursor.execute('select * from books where id = %s', ('1',))
conn.commit()
print(cursor.rowcount)
conn.commit()
cursor.close()

def get_listurl():
    listurl = 'http://www.yousuu.com/booklist?'
    while True:
        try:
            r = requests.get(listurl, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            #####获得书单网址,放进list里,可以是先进先出#######
            #listurl = # 给这个url重新赋值
        except Exception as e:
            print (e)
            break

def get_booklist():
    #FIFO里面获得bookurl。
    '''
    r = requests.get(bookurl, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    #获得page 数量。
    if pages == 1:
    #获得bookid,推荐指数,评语
    else:
        for page in range(1,pages):
            #再获得一次
            '''



