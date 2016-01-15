# -*- coding:utf-8 -*-
"""
2015-01-16 by Camel
https://github.com/daoluan/WXSender-Python/ is acknowledged

"""
import requests
import hashlib
import re

class WeiXin:
	def __init__(self):
		# 公众号登陆账号密码
		self.unm = "your_username"
		self.pwd = "your_password"
		self.token = ''
		self.fakeid = ''
		# 字典存储用户与fakeid的关系
		self.users = {}
		# session自动处理cookies
		self.session = requests.Session()

	def login(self):
		# 登陆
		headers = {
		"Host": "mp.weixin.qq.com",
		"Referer": "https://mp.weixin.qq.com/",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
		}
		data = {
		"username": self.unm,
		"pwd": hashlib.md5(self.pwd).hexdigest(),
		"imgcode": '',
		"f": "json"
		}
		url_login = "https://mp.weixin.qq.com/cgi-bin/login"
		r_login = self.session.post(url_login,data=data,headers=headers)
		try:
			self.token = re.findall("token=(\d*)",r_login.content)[0]
			print "token ",self.token
			if self.token != '':
				print "login success and get token!"
				# 登陆之后转入首页，可去掉
				url_index = "https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=%s" % self.token
				r_index = self.session.get(url_index)
				if r_index.status_code == 200:
					print "get the index"
				else:
					print "get index failed"
			else:
				print "login failed"
		except:
			print "get token error"
		

	def get_fakeid(self):
		# 得到自己的fakeid
		url_fakeid = "https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index&token=%s&lang=zh_CN" % self.token
		r_fakeid = self.session.get(url_fakeid)
		try:
			self.fakeid = re.findall("fakeid=(\d{10})",r_fakeid.content)[0]
			print "get fakeid ",self.fakeid	
		except:
			print "get fakeid error"

	def get_users(self):
		# 得到用户昵称和对应fakeid，写入users字典
		url_user = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=0&type=0&token=%s&lang=zh_CN" % self.token
		r_user = self.session.get(url_user)
		total_users = int(re.findall("totalCount : '(\d*)'",r_user.content)[0])
		page_count = int(re.findall("pageCount : (\d*)",r_user.content)[0])
		page_size = int(re.findall("pageSize : (\d*),",r_user.content)[0])
		user_ids = []
		user_names = []
		for pageidx in xrange(page_count):
			url_userpage = "https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&pageidx=%s&type=0&token=%s&lang=zh_CN" % (str(pageidx),self.token)
			r_userid = self.session.get(url_userpage)
			thepage_user = re.findall("\"id\":\"(.*?){28}\"",r_userid.content)
			thepage_username = re.findall("\"nick_name\":\"(.*?)\"",r_userid.content)
			user_ids += thepage_user
			user_names += thepage_username
		self.users = dict(zip(user_names,user_ids))
		print "get users done"

	def msg2user(self,msg,touserid):
		# 发送消息给用户
		url_msg = "https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json&token=%s&lang=zh_CN" % self.token
		msg_headers = {
		"Host": "mp.weixin.qq.com",
		"Origin": "https://mp.weixin.qq.com",
		"Referer": "https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&tofakeid=%s&token=%s&lang=zh_CN" % (touserid,self.token),
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
		}
		msg_data = {
		"token": self.token,
		"lang": "zh_CN",
		"f": "json",
		"ajax": "1",
		"random": "0.4469808244612068", 
		"type": "1",
		"content": msg,
		"tofakeid": touserid,
		"imgcode": ''
		}
		r_msg = self.session.post(url_msg,data=msg_data,headers=msg_headers)
		if r_msg.status_code == 200:
			err_msg = re.findall("\"err_msg\":\"(.*?)\"",r_msg.content)[0]
			# 发送成功
			if  err_msg == 'ok':
				print "send msg to %s done" % touserid
			# 微信限制，用户48小时内没有主动发送消息，则公众号无法发送消息给该用户
			elif err_msg == 'customer block':
				print "denied because the user hasn't send msg to you in the past 48 hours"
			else:
				print "failed,",err_msg
		else:
			print "send msg to %s failed,and the err_msg %s" % (touserid,r_msg.status_code)

	def run(self,msg,touser):
		self.login()
		self.get_fakeid()
		self.get_users()
		if touser in self.users:
			print "user %s exists" % touser
			self.msg2user(msg,self.users[touser])
		else:
			print "user %s not exists" % touser

wx = WeiXin()
wx.run('test测试','Camel')
