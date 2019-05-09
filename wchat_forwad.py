#encoding=utf-8
# 导入模块
from wxpy import *
import time

import os

if os.path.exists('wxpy.pkl'):
	os.remove('wxpy.pkl')
	
# 初始化机器人，扫码登陆
bot = Bot(cache_path=True,console_qr=1)


src = ensure_one(bot.groups().search('西米露🐰 蜜源团队②群'))
des = ensure_one(bot.groups().search('妙妙的蜜源小队'))
des2 = ensure_one(bot.groups().search('朵儿。蜜源天猫淘宝优惠券'))


@bot.register(src)
def forward_boss_message(msg):
	if 	msg.type =='Sharing':
		return
	time.sleep(5)		
	msg.forward(des)
	msg.forward(des2)

@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    # 接受好友请求
    new_friend = msg.card.accept()
    print('test')
    # 向新的好友发送消息
    new_friend.send('哈哈，我自动接受了你的好友请求')
    
bot.join()
    
	 
