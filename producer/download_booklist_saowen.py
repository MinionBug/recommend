import requests
from bs4 import BeautifulSoup
import mysql.connector

# 将数据库调用放在函数里面
# 将弄个字典,保存cookie这些东西
def ladder(url,pattern):
    #解析url
    print (url)
    r = requests.get(url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    sth = pattern(soup)
    if not sth: #什么都没有取到,说明只有本页面
        return [url]
    else:
        return sth

class Saowen():
    def __init__(self):
        self.start ='http://saowen.net/novellists/index/sort:created/direction:asc/page:'
        self.pages = 106

    def s_p1(self,soup):
        hrefs = []
        for item in soup.find_all('li',class_ = 'item'):
            href = 'http://saowen.net'+item.find('a').get('href')
            hrefs.append(href)
        return hrefs

    def s_p2(self,soup):
        pages = soup.find('div', id='pages').find_all('a')
        if not pages:
            return None
        else:
            links = []
            for page in pages:
                links.append('http://saowen.net'+page.get('href'))
            return links

    def s_p3(self,soup):
        for item in soup.find_all('div',class_ ='item clear'):
            bookid = item.find('a').get('href')[13:]
            ratestar = item.find('span',class_='ratestar')
            if ratestar:
                star = ratestar.get_text()
                num_1 = star.count('★')
                num_half = star.count('☆')
                rate = num_1+0.5*num_half
            else:
                rate = 5
            print([bookid,rate])

    def begin(self):
        for i in range(1, self.pages + 1):
            url = self.start + str(i)
            for j in ladder(url, self.s_p1):
                for k in ladder(j, self.s_p2):
                    ladder(k, self.s_p3)

class Yousuu():
    def __init__(self):
        self.url = 'http://www.yousuu.com/booklist'

    def p1(self,soup):
        shudans = []
        next_page = None
        ###
        trs = soup.find_all('tr', class_='list-item')
        for tr in trs:
            href =tr.find('h4').find('a').get('href')
            shudans.append('http://www.yousuu.com'+href)
        ####
        ul = soup.find('ul', class_='pagination')
        a = ul.find_all('a')[1]
        if a:
            next_page = 'http://www.yousuu.com/booklist?t=' + a.get('onclick')[23:-2]
        ####
        return [shudans,next_page]

    def p2(self,soup):
        books = []
        next_page = None
        ###如果页面数量过多怎么办?
        for div in soup.find_all('div', class_='bd booklist-subject'):
            bookid = div.find('div', class_='title').find('a').get('href')[6:]
            raw_star = div.find('span', class_='num2star').string
            if raw_star:
                star = int(raw_star)
            else:
                star = 0  # 如果没有star,就是0
            cursor.execute('insert into booklist(id,bookid,star) values (%s,%s,%s)', [href[10:], bookid, star])
            # cursor.execute('insert into booklist(id,bookid,star) values (%s,%s,%s)',['5a9d19a57284101a147cb6b6', '12345', 3])
            # print ('3',href[10:],'id:',bookid,star)


        return [books,next_page]

    def begin(self): ####这里出问题了。应该是个循环
        url = self.url
        while True:
            l = ladder(url,self.p1)
            booklists,next_page = l
            for booklist in booklists:
                what = ladder(booklist, self.p2)  ###
                #save_to_db(what)
            if next_page is not None:
                url = next_page
            else:
                break



        p1=ladder(self.url,self.p1)
        if len(p1) == 1:
            shudans = p1
            ladder(shudans,self.p2)
        else:
            shudans,next_page = p1
            ladder(shudans,self.p2)












def save_to_db(listid,bookid,star):
    pass
    #cursor.execute('insert into booklist_g(listid,bookid,star) values (%s,%s,%s)', [listid, bookid, star])

def cookies():
    cookies = {}
    with open('cookies.txt','r') as f:
        for d in  f.read().split(';'):
            name,value = d.split('=')
            cookies[name]= value
    return cookies

cookies = cookies()
headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0'}

#conn = mysql.connector.connect(user='root', password='password', database='Recommend')
#cursor = conn.cursor()

s = Saowen()
print (type(s))
print (type(s.begin()))
#s.start()

#print(cursor.rowcount)
#cursor.close()
#conn.close()


