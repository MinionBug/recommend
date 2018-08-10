import numpy as np
import mysql.connector
import logging

#它娘的。
#bookid到底是以str还是int来保存的?从数据库取出来之后,都是str,但是在放入row。
#配置文件的保存
#np.zeros是否能用空间更小的方式保存。
#将row、line转化为np文件

class Recommend():
    def __init__(self,min_refered):
        # booklist作为所有数据的来源,row书号的集合,line书单号的集合
        self.min_refered = min_refered #书被提及的标准
        self.booklist,self.row,self.line =self.load_from_source()
        self.booknum = len(self.row)


    def load_temp(self):
        #从上一次结果中提取
        self.bbmatrix0 = np.load('../data/bbmatrix.npy')
        self.row0 = np.load('../data/row.npy').tolist()
        self.line0 =np.load('../data/line.npy').tolist()
        self.row0 = [int(x) for x in self.row0]
        logger.info('load data from temp: bbmatrix %s , row %s, line %s' %(len(self.bbmatrix0),len(self.row0),len(self.line0)))

    def mysql_connector(self,sql):
         #'select * from %s' %table
        conn = mysql.connector.connect(user='root', password='password', database='Recommend')
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        logger.info('execute sql: %s' %sql)
        return result

    def load_from_source(self):
        #产生booklist
        booklist = self.mysql_connector('select * from booklist')
        #产生source_row和line数据
        row_source = []
        row = []
        line =[]
        for b in booklist:
            listid = b[0]
            bookid = b[1]  #####注意,这里int了
            if listid not in line:
                line.append(listid)
            if bookid not in row_source:
                row_source.append(bookid)
        print(row_source[:50])
        #计算每本书对应的应用数。
        book_refered_data =[0]*len(row_source)
        for b in booklist:
            bookid2 = b[1]
            location = row_source.index(bookid2)
            book_refered_data[location] += 1
        #筛选,产生真正的row
        for i in range(len(row_source)):
            if book_refered_data[i] > self.min_refered:
                print (int(row_source[i]))
                row.append(int(row_source[i])) #这里被改成int了,但是应该是str
        row.sort()
        print (row[:50]) ############
        logger.info('共有书单%s个,书:%s本,被引用次数大于%s的书%s个。' % (len(line), len(row_source), self.min_refered, len(row)))
        return [booklist,row,line]

    def gen_bpmatrix(self):
        self.bpmatrix = np.zeros((self.booknum, self.booknum))
        #self.bbmatrix = self.load_from_source()+self.load_temp()
        #但这里先假设它不load temp更简单
        for row in self.booklist:
            listid = row[0]
            bookid = row[1]
            if bookid in self.row and listid in self.line:
                r = self.row.index(bookid)  # 定位行,book,要变成数字
                l = self.line.index(listid)  # !!!如果有的话 定位列,书单
                self.bpmatrix[r][l] = row[2]
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

    def gen_bbmatrix(self):
        self.gen_bpmatrix()
        self.bbmatrix =np.zeros((self.booknum,self.booknum))
        logger.info('bbmatrix start:')
        try:
            self.load_temp()
        except:
            self.row0=self.line0=self.bbm=[]
            logger.info('temp not loaded')
        #self.bbmatrix = self.bpmatrix + self.load_temp()
        for i in range(self.booknum - 1):
            for j in range(i+1,self.booknum):
                if self.row[i] in self.row0 and self.row[j] in self.row0:
                    #如果存在于原数据库中,则把旧的数据搬运来
                    i0 = self.row0.index(self.row[i])
                    j0 = self.row0.index(self.row[j])
                    self.bbmatrix[i][j] = self.bbmatrix[j][i]=self.bbmatrix0[i0][j0]
                else:
                    self.bbmatrix[i][j] = self.bbmatrix[j][i] = self.cos(self.bpmatrix[i], self.bpmatrix[j]) # 行相乘
            logger.info('line Done : %s' %i)
            print ('line Done : %s' %i)
        logger.info('bbmatrix赋值完。')

    def topN(self):
        self.gen_bbmatrix()
        ####下面这个数据库要想办法处理
        conn = mysql.connector.connect(user='root', password='password', database='Recommend')
        cursor = conn.cursor()
        cursor.execute('Delete from toprelate')
        logger.info('删掉原有的toprelate数据库')
        for i in range(len(self.row)):
            top_ids = []
            top_ids.append(self.row[i]) #top_ids是返回的结果
            score = zip (self.bbmatrix[i],self.row)
            topbooks = sorted(score, reverse=True)[:self.topN] #[(99,11),(90,2),...]
            for topbook in topbooks:
                top_ids.append(topbook[1])
            t0, t1, t2, t3, t4, t5 = top_ids
            #加入新的
            cursor.execute('insert into toprelate(bookid,top1,top2,top3,top4,top5) values(%s,%s,%s,%s,%s,%s)',
                           [t0, t1, t2, t3, t4, t5])
        ####保存,关闭数据库
        logger.info('toprelate更新完毕')
        conn.commit()
        cursor.close()
        conn.close()
        self.save()

    def save(self):
        np.save('../data/bbmatrix', self.bbmatrix)
        np.save('../data/row',self.row)
        np.save('../data/line',self.line)



logging.basicConfig(filename='producer.log', level=logging.INFO, filemode='a', format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
logger = logging.getLogger(__name__)
r = Recommend(15)
r.topN()



