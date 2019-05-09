#encoding=utf-8
import os,time,re,datetime,json
import urllib.request,requests
from bs4 import  BeautifulSoup
import random
# from InsertData import *
from MailSender import *

key_dict={'10001':'空调','10008':'冰箱','10015':'洗衣机','10034':'厨房小电器','10025':'厨房大电器','10049':'生活家电','10021':'热水/净水','10128':'配件及周边'}
root="https://www.midea.cn/search/search_ajax_data?category_id={0}&str_sort_info=&is_onsale=1&&pageno={1}&pagesize=24&addr_code=440000%2C440100%2C440106&distributor_id=100511&rangelist=%5B%5D"

def add_header(pFile):
	pFile.write('采集日期,分类,商品名,商品编码,价格\n')

def write_data(pFile,type,data_list):
	for item in data_list:
		pFile.write(g_date+","+type+","+item[0]+","+item[1]+","+item[2]+"\n")

def  get_total_nums(url):
	content=requests.get(url).content

	content=str(content, encoding = "utf-8")  
	data=eval(content)#dict
	return data.get('total')


def del_html_space(input_str):
	return  re.sub(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020', ' ', str(input_str)).strip()

def get_product_code(name):
	matched_list = re.findall(r'[a-z,\d,/,\-]+',name,re.I)
	if matched_list == None or len(matched_list) == 0:
		return "None"
	index = 0
	max_len=0

	#取匹配到的最长的字符串
	for i in range(len(matched_list)) :
		if len(matched_list[i] ) > max_len:
			index = i
			max_len = len(matched_list[i])

	return matched_list[index]

def  get_data_by_url(url):
	out_list = list()

	rnd = int(random.random()*5+1)
	time.sleep(rnd)

	content=requests.get(url).content
	content=str(content, encoding = "utf-8")  
	data=eval(content)#dict
	content = data.get('data').replace('\\r\\n',' ').replace('\\','').replace('&yen;','').replace('\u00b3','3')
	soup=BeautifulSoup(content,"html.parser")

	lis = soup.find_all("li")
	for li in lis:
		price_span = li.find("span",{"class":"price"})
		price = price_span.get_text().replace('<em>','').strip(	)

		fn_span = li.find("a",{"class":"fn"})
		name = fn_span.get_text().strip()
		name = del_html_space(name)

		product_code = get_product_code(name)
		out_list.append([name,product_code,price])
	
	return out_list

def checkDownload():
	print(time.strftime('%Y-%m-%d %H:%M:%S'),'process start')
	p_file = open(g_date+'MediaPrice.csv','w')
	add_header(p_file)

	for key in key_dict:
		print(key_dict[key])
		url = root.format(key,1)
		num = get_total_nums(url)
		page = int(num/24) +1
		if num%100 > 0:
			page  = int(num/24) +2

		for i in range(1,page):
			out_list = get_data_by_url(root.format(key,i))
			write_data(p_file,key_dict[key],out_list)

	p_file.close()

def send_mail():

	fileList = os.listdir('.')
	attList=list()

	for file in fileList:
		if file.endswith(".csv") and file.startswith(g_date):
			attList.append(file)

	#发送邮件
	mail_sender =MailSender()
	mail_list = ['64457570@qq.com']	#收件人(列表)
	mail_sender.send(mail_list,'每周美的价格数据自动推送',attList)

if __name__ == "__main__":
	g_date =time.strftime('%Y%m%d')
	while(1):
		if '08' ==time.strftime('%H') and 0 == datetime.datetime.now().weekday():
			g_date =time.strftime('%Y%m%d')
			checkDownload()
			send_mail()
			time.sleep(60*60*5)
		time.sleep(60*30)
