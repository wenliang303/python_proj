#!/usr/bin/python3
 
import pymysql
import time,os

g_date =time.strftime('%Y%m%d')

class InsertData():

	def __init__(self):

		# 打开数据库连接
		self.db = pymysql.connect("132.232.147.117","root","toor","phone_price" )
		 
		# 使用 cursor() 方法创建一个游标对象 cursor
		self.cursor = self.db.cursor()
		# 使用 cursor() 方法创建一个游标对象 cursor

		# 使用 execute()  方法执行 SQL 查询 
		self.cursor.execute("SELECT VERSION()")
		 
		# 使用 fetchone() 方法获取单条数据.
		data = self.cursor.fetchall()
		#print ("Database version : %s " % data)
	

	def getOldDatalist(self):
		fileList = os.listdir('.')
		outList = list()

		for file in fileList:
			if file.endswith(".csv"):
				pFile = open(file,'r')
				contentList =pFile.readlines()
				for item in contentList:
					if '数据来源' in item:
						continue
					tmpList = item.strip().split(',')
					outList.append([tmpList[0],tmpList[1],tmpList[2],tmpList[3],tmpList[4],tmpList[5]])
		
		self.insert_data(outList)

	def insert_data(self,dataList):

		# 使用 execute()  方法执行 SQL 查询 
		for item in dataList:

			insert_cmd ="INSERT INTO price_data ( data_source,collect_date, brand, name, update_date, price ) VALUES ('%s', '%s','%s', '%s', '%s', %d);"%(item[0],item[1],item[2],item[3],item[4],int(item[5]))
			#print(insert_cmd)

			self.cursor.execute(insert_cmd) 
			
		self.db.commit()
		 
		#print ("insert_data done!")

	def delte_data_by_collect_date(self,date):
		del_cmd ="DELETE FROM price_data  where collect_date='%s';"%date

		self.cursor.execute(del_cmd) 			
		self.db.commit()

	def close_db(self):
		# 关闭数据库连接
		print("close_db")
		self.db.close()


if __name__=="__main__":
	ins = InsertData()
	ins.getOldDatalist()
	ins.close_db()