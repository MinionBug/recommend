import numpy as np
import mysql.connector
import logging

#它娘的。
#bookid到底是以str还是int来保存的?从数据库取出来之后,都是str,但是在放入row。
#配置文件的保存
#np.zeros是否能用空间更小的方式保存。
#将row、line转化为np文件

class Recommend2():
    def __init__(self,mini_refered,topN=5):
        self.users = []
        self.items = []
        self.mini_refered = mini_refered
        self.topN = topN

    def mysql_connector(self, sql):
        # 'select * from %s' %table
        cursor.execute(sql)
        result = cursor.fetchall()
        logger.info('execute sql: %s' % sql)
        return result

    def load_from_db(self):
        #数据库
        self.data = self.mysql_connector('select * from booklist')
        #计算user\items,计算次数
        items_with_count = {}
        for x in self.data:
            user = x[0]
            item = x[1]
            if user not in self.users:
                self.users.append(user)
            if item not in self.items:
                self.items.append(item)
                items_with_count[item] = 0
            else:
                items_with_count[item] += 1
        #去掉item中那些未达标的
        for i in items_with_count:
            if items_with_count[i] < self.mini_refered:
                self.items.remove(i)


    def item_user_matrix(self):
        self.iumatrix = np.zeros((len(self.items), len(self.users)))
        for x in self.data:
            user = x[0]
            item = x[1]
            if item in self.items:
                r = self.items.index(item)  # 定位行,book,要变成数字
                l = self.users.index(user)  # !!!如果有的话 定位列,书单
                self.iumatrix[r][l] = x[2]
        logger.info('bpmatrix finish。')

    def cos(self,vector1, vector2):
        #这里打分未经过修正
        dot_product = 0.0
        normA = 0.0
        normB = 0.0
        for a, b in zip(vector1, vector2):
            dot_product += a * b
            normA += a ** 2
            normB += b ** 2
        if normA == 0.0 or normB == 0.0 or dot_product == 0.0:
            return 0
        else:
            return round(dot_product / ((normA ** 0.5) * (normB ** 0.5)) * 100, 2)  # round()返回浮点数x的四舍五入值

    def item_item_matrix(self):
        item_num= len(self.items)
        self.iimatrix =np.zeros((item_num,item_num))
        logger.info('iimatrix start:')
        #self.bbmatrix = self.bpmatrix + self.load_temp()
        for i in range(item_num - 1):
            for j in range(i+1,item_num):
                self.iimatrix[i][j] = self.iimatrix[j][i] = self.cos(self.iumatrix[i], self.iumatrix[j]) # 行相乘
            logger.info('line Done : %s' %i)
            print ('line Done : %s' %i)
        logger.info('iimatrix赋值完。')

    def find_top_related_item(self):
        #每本书,比较,获得其中最大的item。
        for i in range(len(self.items)):
            topitems = []
            items_with_score = zip(self.iimatrix[i], self.items)
            top_item_with_socre = sorted(items_with_score, reverse=True)[:self.topN]  # [(99,11),(90,2),...]
            for topitem in top_item_with_socre:
                topitems.append(topitem[1])
            self.save(self.items[i],topitems)
        logger.info('top赋值完。')
            #进一步保存

    def save(self,*items):
        t0,[t1, t2, t3, t4, t5] = items
        cursor.execute('insert into toprelate2(bookid,top1,top2,top3,top4,top5) values(%s,%s,%s,%s,%s,%s)',
                       [t0, t1, t2, t3, t4, t5])

    def main(self):
        self.load_from_db()
        self.item_user_matrix()
        self.item_item_matrix()
        self.find_top_related_item()



logging.basicConfig(filename='producer.log', level=logging.INFO, filemode='a', format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
logger = logging.getLogger(__name__)
conn = mysql.connector.connect(user='root', password='password', database='Recommend')
cursor = conn.cursor()

r = Recommend2(9)
r.main()

cursor.close()
conn.close()


