use Recommend;

create table toprelate2_yousuu (
    `bookid` varchar(20) not null,
    `top1` varchar(20),
    `top2` varchar(20),
    `top3` varchar(20),
    `top4` varchar(20),
    `top5` varchar(20),
    primary key (`bookid`)
) engine=innodb default charset=utf8;