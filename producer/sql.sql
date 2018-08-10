use Recommend;

create table booklist_g (
    `listid` varchar(20) not null,
    `bookid` varchar(20) ,
    `star` float,
    primary key (`listid`,`bookid`)
) engine=innodb default charset=utf8;


