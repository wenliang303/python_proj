#!/usr/bin/python3
 
import pymysql
import time

g_date =time.strftime('%Y%m%d')

class CreateTable():

	def __init__(self):

		# 打开数据库连接
		self.db = pymysql.connect("132.232.147.117","root","toor","phone_price" )
		 
		# 使用 cursor() 方法创建一个游标对象 cursor
		self.cursor = self.db.cursor()

		# 使用 execute()  方法执行 SQL 查询 
		self.cursor.execute("SELECT VERSION()")
		 
		# 使用 fetchone() 方法获取单条数据.
		data = self.cursor.fetchall()
		print ("Database version : %s " % data)
	
	def create(self):

		sql ="""CREATE TABLE IF NOT EXISTS `price_data`(
					`id` INT UNSIGNED AUTO_INCREMENT,
					`collect_date`	VARCHAR(8)  NOT NULL COMMENT '采集日期',
					`data_source`	VARCHAR(16) NOT NULL COMMENT '数据来源',
					`brand`	        VARCHAR(32) NOT NULL COMMENT '品牌',
					`name`          VARCHAR(64) NOT NULL COMMENT '型号',
					`update_date`   VARCHAR(8)  NOT NULL COMMENT '更新日期',
					`price`         INT         NOT NULL COMMENT '价格',
					PRIMARY KEY ( `id` )
				)ENGINE=InnoDB auto_increment=1 DEFAULT CHARSET=UTF8MB4;"""
		self.cursor.execute(sql)
		self.db.commit()
	
	def close_db(self):
		# 关闭数据库连接
		print("close_db")
		self.db.close()


if __name__=="__main__":
	ins = CreateTable()
	ins.create()
	ins.close_db()