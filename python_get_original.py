#encoding=utf-8
import os,time,re,time,json
import urllib.request,requests
from bs4 import  BeautifulSoup

from InsertData import *
from MailSender import *

filter=['机器人','ipad','wifi','平板','手环','手表','寸','matebook','watch','笔记本','充电器','鼠标','耳机','游戏本',
		'b3','b5','演示机','m3','手柄','耳机']
brand_list= ['华为','华为G网','小米','苹果','荣耀','OPPO','vivo','步步高(vivo)']

def add_header(pFile):
	pFile.write('数据来源,采集日期,品牌,型号,更新日期,价格\n')

def get_formate_date(date_in):

	if "(" in date_in and ")" in date_in:
		date_in = date_in.split("(")[1].split(")")[0]

	dateList = re.findall(r"\d+\.?\d*",date_in)
	date = "".join(str("%02d" % int(a.strip())) for a in dateList)

	if date ==None or date =="":
		date = g_date #解析不到日期，取最新当前日期
	return date

def is_item_in_filter(product):
	for item in filter:
		if item in product.lower():		
			return True

	return False

def updateprice(outdict,brand,phone,price):

	if phone in outdict:
		if brand ==outdict[phone][0] and price < outdict[phone][1]:
			outdict[phone][1] = price #update to lower price
	else:
		outdict[phone]=[brand,price]

def parse_ttcgw():
	url="http://www.ttcgw.com/data/itemPrice.xml"
	content=requests.get(url).content
	soup = BeautifulSoup(content, "html.parser")
	outdict= dict()#{phone:[brand,price]}

	date = get_formate_date(soup.find("items").get('date'))
	print("天天采购网：date="+date+url)
	
	for tr in soup.find_all('item'):#使用字典去重
		brand = tr.get('brand').strip()
		phone = tr.get('type')
		price = tr.get('price').strip()
		if price=='':
			price= 0
		else:
			price = int(tr.get('price'))

		if brand in brand_list:
			if not is_item_in_filter(phone):
				if brand == '华为' and '荣耀' in phone:
					brand = '荣耀'
					phone = phone.replace('荣耀 ', '')
				
				updateprice(outdict,brand,phone,price)

		if brand =='其他品牌':
			if 'vivo' in phone and not is_item_in_filter(phone):
				brand ='vivo'
				updateprice(outdict,brand,phone,price)

			if ('OPPO' in phone or 'Find X' in phone) and not is_item_in_filter(phone):
				brand ='oppo'
				updateprice(outdict,brand,phone,price)

	p_file = open(g_date+"ttcgw.csv",'w')
	add_header(p_file)

	new_dict= dict()#transfer to {brand:[[phone1,price],[phone2,price]]}
	for phone in outdict:
		if outdict[phone][0] not in  new_dict:
			new_dict[outdict[phone][0]] = list()
		new_dict[outdict[phone][0]].append([phone,str(outdict[phone][1])])

	for brand in new_dict:
		for item in new_dict[brand]:
			p_file.write("天天采购网,"+g_date+","+brand+","+item[0]+","+date+','+item[1]+"\n")	
	p_file.close()

def parse_huiyoutongxun():

	id_brand_dict={"16":"华为","6":"苹果","13":"小米","46":"oppo","47":"vivo"}#
	url = "http://www.sjpif.net/price/price.loading.php?id=%s"

	p_file = open(g_date+"huiyou.csv",'w')
	add_header(p_file)

	for key in id_brand_dict:
		
		outlist = parse_sjpif(url%key,id_brand_dict[key])# 按品牌分类，不同品牌id不同
		for line in outlist:
			p_file.write("惠友通讯,"+g_date+","+line[0]+","+line[1]+","+line[2]+","+line[3]+"\n")

	p_file.close()

def parse_sjpif(url,brand):
	content=requests.get(url).content
	soup = BeautifulSoup(content, "html.parser")
	outlist = list()

	time.sleep(2)
	#找第一个有效的table的时间作为当前时间
	tables = soup.find_all('table')
	if tables == None or len(tables) <=1:
		return outlist

	table = soup.find_all('table')[1]
	date_str =table.find('tr').find('td').get_text()
	date = get_formate_date(date_str)
	print('惠友通讯 date='+date+url)
	#print(date)

	tbs = soup.find_all("table",{"class":"price_table_box"})
	for tb in tbs:
		for tr in tb.find_all("tr"):
			if tr.get('style') !=None:
				tds = tr.find_all('td')

				font_tag =tds[0].find('font')#获取产品名，第一个td的第一个font
				product = font_tag.get_text().strip()
				if  is_item_in_filter(product):
					continue
				version = tds[0].find('font',{"style":'float:right;font-weight:bold;border-left:1px dashed #ccc;padding-left:6px;text-align:left;color: #232323;'})

				if version != None:
					fonts_price = tds[1].find('font',{"style":"float:right;font-weight:bold;color:#f33a36;"})
					if fonts_price == None :
						fonts_price = tds[1].find('font',{"style":"float:right;font-weight:bold;text-decoration: line-through; color:blue;"})
					price =  fonts_price.get_text().strip()#获取价格 第二td的第一个font
					outlist.append([brand,product, date,price])
	return outlist

def get_kuang_zhuang_latest_url(root_url):
	content=requests.get(root_url).content
	soup=BeautifulSoup(content,"html.parser")
	a_tags  =soup.find("a",{"onclick":"atarget(this)"})#取最上面的超链接

	return a_tags.get('href')

def del_html_space(input_str):
	return  re.sub(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020', ' ', str(input_str)).strip()

def get_price(prices):
	prices = prices.strip()

	if prices =='0' or prices =='':#0和空数据直接返回0
		return 0

	priceList = prices.split('/')
	newList = list()
	for a in priceList:
		a = a.strip()
		tmpList = re.findall(r"\d+",a)#查询数字，避免出现字符

		if len(tmpList) == 0:#没有数字继续
			continue
		else:
			if int(tmpList[0]) !=0:
				newList.append(int(tmpList[0]))

	if len(newList) == 0:
		return 0

	return min(newList)

def parse_kangzhung_by_url(url):
	#url = "http://www.kanzan.cn/forum.php?mod=viewthread&tid=6907&extra=page%3D1"
	time.sleep(1)
	content=requests.get(url).content
	soup = BeautifulSoup(content, "html.parser")
	outlist = list()
	date  =soup.find('span',{'id':'thread_subject'}).get_text()
	date = get_formate_date(date)

	print('康庄数码 安卓 date='+date+url)

	trs = soup.find_all('tr')#找到所有的tr标签
	brand = None
	i=0
	for tr in trs: 
		tds = tr.find_all('td')
		if tds == None or len(tds)==0 :#没有数据的直接跳过
			continue
		clss = tds[0].get('class')
		if clss != None  and 'scbar_type_td' == tds[0].get('class')[0]:#去掉搜索框
			continue

		colspan= tds[0].get('colspan') 
		if colspan != None:#colspan的列，更新品牌，继续处理下个tr里的产品
			brand =tds[0].get_text()
			brand = del_html_space(brand).replace('Mate 系列','华为')
			brand = del_html_space(brand).replace('P 系列','华为')
			brand = del_html_space(brand).replace('nova 系列','华为')
			brand = del_html_space(brand).replace('麦芒 系列','华为')
			brand = del_html_space(brand).replace('畅享 系列','华为')
			brand = del_html_space(brand).replace('Honor 荣耀系列','荣耀')
			brand = del_html_space(brand).replace('Honor 畅玩 系列','荣耀')
			continue

		if brand not in brand_list:
			continue

		if len(tds)==3:#找到正确的产品行，取第一列和第三列
			product_tmp = tds[0].get_text()
			product = del_html_space(product_tmp)
			price = get_price(tds[2].get_text())

			if  is_item_in_filter(product):
				continue
			outlist.append([brand,product,date,str(price)])
	return outlist

def parse_kangzhung_iphone(url):
	content=requests.get(url).content
	soup = BeautifulSoup(content, "html.parser")
	outlist = list()
	date  =soup.find('span',{'id':'thread_subject'}).get_text()
	date = get_formate_date(date)

	print('康庄数码 苹果 date='+date+url)

	tbs = soup.find_all("table",{"class":"t_table"})
	for tb in tbs:
		trs = tb.find_all('tr')
		typs = ""
		product=''
		for i in range(len(trs)):
			tds = trs[i].find_all('td')

			if i == 0:
				typs = tds[0].get_text()
			else:
				if len(tds) == 1:
					product = del_html_space(tds[0].get_text()) 

			if '全新机' not in typs:
				break

			if len(tds) == 2:
				product = del_html_space(tds[0].get_text())


			if ('国行' not in product) or  ('原封' not in product):
				continue

			if len(tds) == 3:
				phone = del_html_space(tds[0].get_text())
				price = get_price(tds[2].get_text())
				outlist.append([product +" "+ phone,date,str(price)])

	return outlist

def parse_kangzhung():
	p_file = open(g_date+'kangzhuang.csv','w')
	add_header(p_file)

	###处理安卓报价
	url = get_kuang_zhuang_latest_url("http://www.kanzan.cn/forum.php?mod=forumdisplay&fid=2&page=1")#在主页上获取最新报价的网页地址
	#url = 'http://www.kanzan.cn/forum.php?mod=viewthread&tid=6971&extra=page%3D1'
	if url == None:
		print("parse_kangzhung: Error, no data to run")
		return list()

	outlist = parse_kangzhung_by_url(url)
	for line in outlist:
		p_file.write("康庄数码,"+g_date+","+line[0]+","+line[1]+","+line[2]+","+line[3]+"\n")

	###处理苹果报价
	iphone_url=get_kuang_zhuang_latest_url('http://www.kanzan.cn/forum.php?mod=forumdisplay&fid=71')
	iphoneList = parse_kangzhung_iphone(iphone_url)
	for line in iphoneList:
		p_file.write("康庄数码,"+g_date+","+'苹果'+","+line[0]+","+line[1]+","+line[2]+"\n")
	p_file.close()

def get_min_price(prices):
	min_price = 999999
	for price in prices:
		str(prices[price][1]).replace('.0','')
		if prices[price][1]< min_price:
			min_price = prices[price][1]

	return str(min_price).replace('.0','')

def get_yidao_sessionid():
	login_url='http://b2bs.qianchi365.com/client/login/login?loginName=13751121514&password=e10adc3949ba59abbe56e057f20f883e'
	content=requests.get(login_url).content

	result=str(content, encoding = "utf-8")  
	info=eval(result)
	return info.get('ticket')

def parse_yidao():

	session = get_yidao_sessionid()
	print("易道(仟驰科技) session ="+session)

	data_url="http://b2bs.qianchi365.com/client/commodityReport;jsessionid={0}?type=001001001".format(session)
	content=requests.get(data_url).content

	content=str(content, encoding = "utf-8")  
	data=eval(content)#dict
	brands = data.get('obj')

	p_file=open(g_date+"yidao.csv",'w')
	add_header(p_file)

	for brand in brands:

		if brand not in  brand_list:
			continue
		
		products = brands[brand]
		for product in products:
			prices = products[product]
			#print(product,"=====",brands[brand][product])
			price =get_min_price(prices)
			brand   = brand.replace('步步高(vivo)','vivo')
			product = product.replace('步步高(vivo)','')

			if  not  is_item_in_filter(product):
				p_file.write('易道(仟驰科技),'+g_date+","+brand+","+product+","+g_date+","+price+"\n")
			#print(brand,product,price)
	p_file.close()

def checkDownload():
	print(time.strftime('%Y-%m-%d %H:%M:%S'),'process start')
	parse_ttcgw()#天天采购网
	parse_huiyoutongxun()
	parse_kangzhung()#分国行和苹果，苹果不好解析。
	parse_yidao()

def insert_data():
	ins = InsertData()
	ins.delte_data_by_collect_date(g_date)

	fileList = os.listdir('.')
	outList = list()
	attList=list()

	for file in fileList:
		if file.endswith(".csv") and file.startswith(g_date):
			attList.append(file)
			pFile = open(file,'r')
			contentList =pFile.readlines()
			for item in contentList:
				if '数据来源' in item:
					continue
				tmpList = item.strip().split(',')
				outList.append([tmpList[0],tmpList[1],tmpList[2],tmpList[3],tmpList[4],tmpList[5]])
	
	ins.insert_data(outList)
	ins.close_db()

	#发送邮件
	mail_sender =MailSender()
	mail_list = ['64457570@qq.com']	#收件人(列表)
	mail_sender.send(mail_list,"每日手机价格数据自动推送",attList)
	
if __name__ == "__main__":
	g_date =time.strftime('%Y%m%d')
	while(1):
		if '20' ==time.strftime('%H'):
			g_date =time.strftime('%Y%m%d')
			checkDownload()
			insert_data()
			time.sleep(60*60*5)
		time.sleep(60*30)