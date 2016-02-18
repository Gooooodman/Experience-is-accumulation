


#查询6月份活跃度
select count(distinct role_id) from t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-06-01 00:00:00") and UNIX_TIMESTAMP("2015-06-30 23:59:59");


/*安卓、应用宝各要一份
1、8.8-8.9 全服充值玩家
ID、角色名、等级、VIP、充值金额*/

select dr.id,dr.name,dr.lvl,dr.total_payment from dzmo_admin_qq_1.t_log_pay dt join  dzmo_qq_1.role dr on  dr.id = dt.role_id \ 
where dt.m_time BETWEEN UNIX_TIMESTAMP("2015-08-08 00:00:00") and UNIX_TIMESTAMP("2015-08-09 23:59:59")  order by dr.total_payment desc;


/*2、8.7-8.9 全服参与守护系统的玩家
ID、角色名、等级、VIP等级、守护等级*/

select dt.role_id,dr.name,dr.lvl,dr.vip,sum(dt.money)  from dzmo_admin_ios_yueyu_1.t_log_diam dt join dzmo_ios_yueyu_1.role dr on dt.role_id = dr.id \ 
where dt.m_type = 40077 and dt.m_time BETWEEN UNIX_TIMESTAMP("2015-08-07 00:00:00") and UNIX_TIMESTAMP("2015-08-09 23:59:59") group by dt.role_id;




#查婚宴
select role_a,role_b from t_log_marry where m_type >= 100 and m_time BETWEEN UNIX_TIMESTAMP("2015-08-18 00:00:00") and UNIX_TIMESTAMP("2015-08-20 23:59:59");

select m.role_a,r.name as aname,m.role_b,r1.name as bname from t_log_marry m join dzmo_ios_yueyu_12.role r on m.role_a = r.id left join dzmo_ios_yueyu_12.role r1 on m.role_b = r1.id where m.m_type >= 100 and m.m_time BETWEEN UNIX_TIMESTAMP("2015-08-18 00:00:00") and UNIX_TIMESTAMP("2015-08-20 23:59:59");



#查渠道登陆总人数
select count(distinct account_name) as total,platform from t_log_access where m_time BETWEEN UNIX_TIMESTAMP("2015-08-10 00:00:00") and UNIX_TIMESTAMP("2015-08-16 23:59:59") group by platform; 

select count(distinct account_name) as renshu,platform from t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-08-10 00:00:00") and UNIX_TIMESTAMP("2015-08-16 23:59:59") group by platform; 




#查渠道登陆总人数

select count(distinct account_name) as 人数,platform as 渠道 from t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-10-00 00:00:00") and UNIX_TIMESTAMP("2015-10-31 23:59:59") group by platform; 

#查渠道充值总人数
select count(distinct account_name) as 人数,platform as 渠道 from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-08-10 00:00:00") and UNIX_TIMESTAMP("2015-08-31 23:59:59") group by platform; 







select count(distinct account_name) as 人数,platform as 渠道 from t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-09-01 00:00:00") and UNIX_TIMESTAMP("2015-09-30 23:59:59") group by platform; 
select count(distinct account_name) as 人数,platform as 渠道 from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-09-01 00:00:00") and UNIX_TIMESTAMP("2015-09-30 23:59:59") group by platform; 













610263:50
100070:97



#坐骑的获得人数
select count(distinct role_id),m_type,item_id from t_log_items where m_type = 10003;

#道具表
select count(distinct role_id),item_id,m_type from t_log_items where item_id = 610263;




select count(item_id) as 数量 ,count(item_id)*money as 总价 from t_log_mall where item_id = 50 and m_time BETWEEN UNIX_TIMESTAMP("2015-09-29 00:00:00") and UNIX_TIMESTAMP("2015-10-08 23:59:59"); 


select count(item_id) as 数量 ,count(item_id)*money as 总价 from t_log_mall where item_id = 97 and m_time BETWEEN UNIX_TIMESTAMP("2015-09-29 00:00:00") and UNIX_TIMESTAMP("2015-10-08 23:59:59"); 




#坐骑的获得人数
use dzmo_qq_125;
select count(role_id) from mount where mount_id = 10001 and m_time BETWEEN UNIX_TIMESTAMP("2015-09-29 00:00:00") and UNIX_TIMESTAMP("2015-10-08 23:59:59");
select count(role_id) from mount where mount_id = 10002 and m_time BETWEEN UNIX_TIMESTAMP("2015-09-29 00:00:00") and UNIX_TIMESTAMP("2015-10-08 23:59:59");
select count(role_id) from mount where mount_id = 10003 and m_time BETWEEN UNIX_TIMESTAMP("2015-09-29 00:00:00") and UNIX_TIMESTAMP("2015-10-08 23:59:59");









select m.role_id,r.name,m.star,m.lvl from mount m  join role r on  m.role_id = r.id  where m.mount_id = 10002 order by m.star desc;

#每个玩家获得以下两种道具的数量

SELECT role_id,COUNT(*) FROM  t_log_items where item_id = 150002 group by role_id order by COUNT(*) desc;









select distinct l.role_id,r.wing,r.wing_awake_level from dzmo_admin_en_1.t_log_login l join dzmo_en_1.role r on l.role_id = r.id where l.m_time BETWEEN UNIX_TIMESTAMP("2015-10-23 00:00:00") and UNIX_TIMESTAMP("2015-10-25 23:59:59") and r.wing in (50001,50002,50003,50004,50005,50006,50007,50008,50009,50010,50011,50012,50013,50014,50015,50016,50017,50018,50019,50020,50021);







#英语-GP1渠道-8月份的充值详单（需要区分google、mol、bluepay这3个付款方式）对账用

select role_id , role_name, order_id , pay_money  from t_log_pay where platform = 001003 and m_time BETWEEN UNIX_TIMESTAMP("2015-08-01 00:00:00") and UNIX_TIMESTAMP("2015-08-31 23:59:59")  order by order_id  ,pay_money desc;


select role_id , role_name, order_id , pay_money ,m_year, m_month,m_day,m_hour from t_log_pay where platform = 001003 and m_time BETWEEN UNIX_TIMESTAMP("2015-08-01 00:00:00") and UNIX_TIMESTAMP("2015-08-31 23:59:59")  order by order_id  ,pay_money desc;













#一周活跃玩家的装备品阶
   ##一周活跃玩家
select count(distinct role_id) from t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-06-01 00:00:00") and UNIX_TIMESTAMP("2015-06-30 23:59:59");
   ##一个玩家的装备品阶
select id ,role_id,goods_id,pos,repos,color from goods  where repos =2 and pos in(1,2,3,4,5,6,7) and  role_id = 8589944809;

select role_id,goods_id,pos,repos,color from dzmo_en_1.goods  where repos =2 and pos in(1,2,3,4,5,6,7) and  \
role_id in (select distinct role_id from dzmo_admin_en_1.t_log_login where m_time BETWEEN UNIX_TIMESTAMP("2015-10-12 00:00:00") and UNIX_TIMESTAMP("2015-10-19 23:59:59"));


/usr/bin/mysql -p`cat /data/save/mysql_root` -e "select role_id,goods_id,pos,repos,color from dzmo_en_${id}.goods  where repos =2 and pos in(1,2,3,4,5,6,7) and role_id in (select distinct role_id from dzmo_admin_en_${id}.t_log_login where m_time BETWEEN UNIX_TIMESTAMP(\""2015-10-12 00:00:00\"") and UNIX_TIMESTAMP(\""2015-10-19 23:59:59\""));"






#10月充值与人数

echo "/usr/bin/mysql -p`cat /data/save/mysql_root` -e 'use dzmo_admin_en_${d};select count(distinct account_name) as 人数,platform as 渠道 from  t_log_login where m_time BETWEEN UNIX_TIMESTAMP(\""2015-10-00 00:00:00\"") and UNIX_TIMESTAMP(\""2015-10-31 23:59:59\"") group by platform; '> ${d}_renshu.txt"
echo "/usr/bin/mysql -p`cat /data/save/mysql_root` -e 'use dzmo_admin_en_${d};select count(distinct account_name) as 人数,platform as 渠道 from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP(\""2015-10-00 00:00:00\"") and UNIX_TIMESTAMP(\""2015-10-31 23:59:59\"") group by platform;' > ${d}_chongzhi.txt"









#英语-GP1渠道-8月份的充值详单（需要区分google、mol、bluepay这3个付款方式）对账用

select role_id , role_name, order_id , pay_money ,m_year, m_month,m_day,m_hour from t_log_pay where platform = 001008 and m_time BETWEEN UNIX_TIMESTAMP("2015-10-01 00:00:00") and UNIX_TIMESTAMP("2015-10-31 23:59:59")  order by order_id  ,pay_money desc;








#全服装备精炼7星、8星、9星、及以上的玩家数据量
select count(distinct role_id) from goods where repos =2 and pos in(1,2,3,4,5,6,7) refin = 9 ;

select count(distinct role_id) from goods where repos =2 and pos in(1,2,3,4,5,6,7) refin > 9 ;









#详单
select role_id , role_name, order_id , pay_money from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-10-10 00:00:00") and UNIX_TIMESTAMP("2015-10-10 23:59:59")  order by order_id  ,pay_money desc;

#每个人的充值总数
select role_id , role_name ,sum(pay_money) from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-10-10 00:00:00") and UNIX_TIMESTAMP("2015-10-10 23:59:59")  group by role_id;

# 充值>500的玩家
select role_id , role_name ,sum(pay_money) from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-11-11 00:00:00") and UNIX_TIMESTAMP("2015-11-11 23:59:59")  group by role_id having sum(pay_money) >500 ;





# 充值>1000的玩家 排序
#11号 > 1000 
select role_id , role_name,platform ,sum(pay_money) as p from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-11-11 00:00:00") and UNIX_TIMESTAMP("2015-11-11 23:59:59")  group by role_id having p >1000 order by p;

#12号 > 1000 
select role_id , role_name,platform ,sum(pay_money) as p from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-11-12 00:00:00") and UNIX_TIMESTAMP("2015-11-12 23:59:59")  group by role_id having p >1000 order by p;

#11-12号 > 1000 
select role_id , role_name,platform ,sum(pay_money) as p from t_log_pay where m_time BETWEEN UNIX_TIMESTAMP("2015-11-11 00:00:00") and UNIX_TIMESTAMP("2015-11-12 23:59:59")  group by role_id having p >1000 order by platform ,p;




echo "/usr/bin/mysql -p`cat /data/save/mysql_root` -e 'use dzmo_admin_en_$db1;select role_id , role_name, order_id , pay_money ,m_year, m_month,m_day,m_hour from     t_log_pay where platform = 001008 and m_time BETWEEN UNIX_TIMESTAMP(\""2015-10-01 00:00:00\"") and UNIX_TIMESTAMP(\""2015-10-31 23:59:59\"")  order by order_id  ,pay_money desc; ' > ${d}_chongzhi.txt"







#每个角色使用 9朵 99朵 999朵 鲜花的数量

select role_id,sum(item_number) from t_log_items where item_id = 100060 and m_type =20088 and m_time BETWEEN UNIX_TIMESTAMP("2015-11-25 00:00:00") and UNIX_TIMESTAMP("2015-11-26 14:00:00") group by role_id order by sum(item_number);

select role_id,sum(item_number) from t_log_items where item_id = 100061 and m_type =20088 and m_time BETWEEN UNIX_TIMESTAMP("2015-11-25 00:00:00") and UNIX_TIMESTAMP("2015-11-26 14:00:00") group by role_id order by sum(item_number);

select role_id,sum(item_number) from t_log_items where item_id = 100062 and m_type =20088 and m_time BETWEEN UNIX_TIMESTAMP("2015-11-25 00:00:00") and UNIX_TIMESTAMP("2015-11-26 14:00:00") group by role_id order by sum(item_number);


#select role_id,sum(item_number) from t_log_items where item_id = 100060 and m_type =20088 and m_time BETWEEN UNIX_TIMESTAMP("2015-11-25 00:00:00") and UNIX_TIMESTAMP("2015-11-26 14:00:00") and role_id = 8589939681;




充值详单渠道列表
001001
001002
001003
001004
001005
001006
001007
001008
001010
001011
001012
001013





#台湾充值
echo "/usr/bin/mysql -p`cat /data/save/mysql_root` -e 'use dzmo_admin_tw_1;select role_id , role_name, order_id , pay_money ,m_year, m_month,m_day,m_hour from     t_log_pay where  m_time BETWEEN UNIX_TIMESTAMP(\""2015-11-01 00:00:00\"") and UNIX_TIMESTAMP(\""2015-11-30 23:59:59\"")  order by order_id  ,pay_money desc; ' > chongzhi.txt"









select id,order_id,account_name,role_id,request from t_log_pay_request_002002 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") limit 10;




select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_002002 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") limit 10;


select count(request) from t_log_pay_request_002002 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59");





mysql -p`cat /data/save/mysql_root` -e 'select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_002002 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP(\"2016-01-31 23:59:59\") limit 10;'






mysql -p`cat /data/save/mysql_root` -e 'use dzmo_gateway;select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_002001 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") ;' > request_002001.log


mysql -p`cat /data/save/mysql_root` -e 'use dzmo_gateway;select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_002003 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") ;' > request_002003.log


mysql -p`cat /data/save/mysql_root` -e 'use dzmo_gateway;select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_002004 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") ;' > request_002004.log

mysql -p`cat /data/save/mysql_root` -e 'use dzmo_gateway;select order_id,account_name,role_id,agent_name,server_id,channel,request from t_log_pay_request_292001 where m_time BETWEEN UNIX_TIMESTAMP("2016-01-01 00:00:00") and UNIX_TIMESTAMP("2016-01-31 23:59:59") ;' > request_292001.log



