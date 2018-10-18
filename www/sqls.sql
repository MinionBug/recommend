use Recommend;

create table if not exists book(
   bid INT auto_increment NOT NULL,
   title VARCHAR(40) NOT NULL,
   author VARCHAR(40) NOT NULL,
   words VARCHAR(20),
   finished VARCHAR(40),
   link VARCHAR(60),
   PRIMARY KEY (bid)
) engine=innodb default charset=utf8;

create table if not exists user(
   uid INT auto_increment NOT NULL,
   email VARCHAR(50) NOT NULL,
   passwd VARCHAR(50) NOT NULL,
   name VARCHAR(50) NOT NULL,
   created_at FLOAT NOT NULL,
   PRIMARY KEY (uid)
) engine=innodb default charset=utf8;

create table if not exists tag(
   tid VARCHAR(50) NOT NULL,
   uid INT NOT NULL,
   bid INT NOT NULL,
   tag VARCHAR(30),
   created_at FLOAT NOT NULL,
   PRIMARY KEY (tid)
) engine=innodb default charset=utf8;

create table if not exists comment(
   cid VARCHAR(50) NOT NULL,
   uid INT NOT NULL,
   bid INT NOT NULL,
   readed VARCHAR(10),
   star INT,
   comment TEXT,
   created_at FLOAT NOT NULL,
   PRIMARY KEY (cid)
) engine=innodb default charset=utf8;

create table if not exists bookrecommend(
   bid INT NOT NULL,
   title VARCHAR(40) NOT NULL,
   author VARCHAR(40) NOT NULL,
   t1 INT NOT NULL,
   t2 INT ,
   t3 INT ,
   t4 INT ,
   t5 INT ,
   t6 INT ,
   t7 INT ,
   t8 INT ,
   ut1 INT NOT NULL,
   ut2 INT ,
   ut3 INT ,
   ut4 INT ,
   ut5 INT ,
   ut6 INT ,
   ut7 INT ,
   ut8 INT ,
   PRIMARY KEY (bid)
) engine=innodb default charset=utf8;

create table if not exists userrecommend(
   uid INT NOT NULL,
   t1 INT NOT NULL,
   t2 INT,
   t3 INT,
   t4 INT,
   t5 INT,
   t6 INT,
   t7 INT,
   t8 INT,
   PRIMARY KEY (uid)
) engine=innodb default charset=utf8;


