#!/usr/bin/python3
#-*-coding:UTF-8-*-

import smtplib,time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
 
class MailSender():
	def __init__(self):
		self.mail_host="smtp.163.com"			                    #使用的邮箱的smtp服务器地址
		self.sender="wenliangzh_303@163.com"
		self.auth_code="wenliangzh303"

	def send_mail(self, to_list, sub, content, attchList):

		me="William"+"<"+self.sender+">"
		msg = MIMEMultipart()
		#msg = MIMEText(content,_subtype='plain')
 		#msg['Subject'] = sub
		msg['Subject'] = Header(sub, 'utf-8')
		msg['From'] = me
		msg['To'] = ";".join(to_list)		#将收件人列表以‘；’分隔

		#邮件正文内容
		msg.attach(MIMEText(content, 'plain', 'utf-8'))
		
		# 构造附件
		for file in attchList:

			att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
			att["Content-Type"] = 'application/octet-stream'
			# 这里的filename可以任意写，写什么名字，邮件中显示什么名字
			att["Content-Disposition"] = 'attachment; filename="%s"'%file
			msg.attach(att)

		try:
			server = smtplib.SMTP()
			server.connect(self.mail_host)							#连接服务器
			server.login(self.sender,self.auth_code)	#登录操作,密码是授权码，而不是邮箱登录密码
			server.sendmail(me, to_list, msg.as_string())
			server.close()
			return True

		except Exception as e:
			print (str(e))
			return False

	def send(self, mailto_list,subject,attchList):
		if self.send_mail(mailto_list,subject,"请查收，谢谢！", attchList):  #邮件主题和邮件内容
			print (time.strftime("%Y-%m-%d %H:%M:%S"),"send done!")

if __name__=="__main__":
	ins = MailSender()
	ins.send()
