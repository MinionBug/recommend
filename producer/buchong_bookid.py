import requests
from bs4 import BeautifulSoup
import mysql.connector


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
rbookurl = 'http://www.yousuu.com/book/'
def download(i):
    try:
        bookurl = rbookurl + str(i)
        print(bookurl)
        r = requests.get(bookurl,timeout = 5)
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
        print('insert:', i, title, author, word_count, updated)
    except Exception as e:
        print('connect error', e)

def get_by_bookid(i): #这里要try,以防超过了50000的范围
    cursor.execute('select * from books where id = %s',(int(i),))
        # cursor.execute('select * from books where id = %s', ('1',))
    result = cursor.fetchone()
    if result:
        print ('exist:',i)
        return True
    else:
        print ('no exist',i)
        return False



conn = mysql.connector.connect(user='root', password='password', database='Recommend')
cursor = conn.cursor()

def get_row():
    cursor.execute('select * from booklist')
    booklist = cursor.fetchall()
    # 产生source_row和line数据
    row_source = []
    for b in booklist:
        bookid = b[1]
        if bookid not in row_source:
            row_source.append(bookid)
    return row_source



for bookid in get_row():
    print (bookid)
    if not get_by_bookid(bookid):
        download(bookid)


conn.commit()
cursor.close()
