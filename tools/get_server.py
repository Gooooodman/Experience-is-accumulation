#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__="lupuxiao" 

'''
通过后台api,下载xml文件进行解析

功能：
	获取渠道ip(去重)
	获取服的信息：平台-ip-id

'''
import os
import urllib2
from parse_xml import parse_xml
import ConfigParser




class get_server():
	def __init__(self,show_log=False,writefile=False):
		self.show_log=show_log
		self.writefile=writefile


	def down_xml(self,url,name):
		'''下载url命令为name.xml'''
		filename="/tmp/%s.xml"%name
		if os.path.exists(filename):
			os.remove(filename)

		file=open(filename,'w')
		try:
			res=urllib2.urlopen(url)
			xml=res.read()	
			file.write(xml)
			if self.show_log:
				print "\033[1;33m已保存 %s 在本地.\033[0m"%filename
			#print url
		except Exception as err:
			print "下载\033[1;31m%s\033[0m地址保存%s失败!  信息: %s"%(url,filename,str(err))
			exit()	
		finally: 
			file.close()

	def get_repeat_ip(self,xmlfile):
		try:
			xml=parse_xml(xmlfile,show_log=False)
			#判断文件
			xml.xml_exists()
			if self.writefile:
				name=xmlfile.split(".")[0]
				namefile="%s_ip.txt"%name
				if os.path.exists(namefile):
					os.remove(namefile)			
				file=open(namefile,'w+')
			xml.get_root()
			childs=xml.get_element_children(xml.root)
			ips=[]
			for child in childs:
				ips.append(child.get("ip"))
			ips=sorted(list(set(ips)))
			if self.show_log:
				for ip in ips:
					print ip 
					if self.writefile:
						file.write(ip)
						file.write("\n")
			if self.writefile:
				file.close()					
			return ips
		except Exception as err:
			print err

			#yy.xml yy 和ios_yueyu 在一起统计
	def get_info(self,xmlfile):
		#返回字典
		try:
			xml=parse_xml(xmlfile,show_log=False)
			#判断文件
			xml.xml_exists()		
			xml.get_root()
			all={}
			#dirc={}
			childs=xml.get_element_children(xml.root)
			for child in childs:
				plat=child.get("platform")
				cid=child.get("id")
				ip=child.get("ip")
				sshport=int(child.get("port"))
				mark=plat+"_s"+cid
				dirc={mark:{}}
				dirc[mark].update({"ip":ip,"id":cid,"platform":plat,"port":sshport})
				all.update(dirc)
			if self.show_log:
				for agent in all:
					print agent
			return all
		except Exception as err:
			print "获取失败.错误如下:",err

			#yy.xml yy 和ios_yueyu 分开统计
	def get_plat_info(self,xmlfile,name):		
		all = self.get_info(xmlfile)
		alls = {}
		for p in all:
			plat=all[p].get("platform")
			if name == "android":
				name = "ios_yueyu"
			if name == plat:
			 	id=all[p].get('id')
			 	server="%s_s%s"%(plat,id)
			 	dirc={server:{}}
			 	dirc[server].update(all[p])
				alls.update(dirc)
		return alls		

	def get_plat_ip_port(self,xmlfile,name):
		all=self.get_plat_info(xmlfile,name)
		alls={}
		for p in all:
			ip=all[p].get("ip")
			port=all[p].get("port")
			dirc={ip:{}}
			dirc[ip].update({"ip":ip,"port":port})
			alls.update(dirc)
		return alls

	def down_all_xml(self):
		cf = ConfigParser.ConfigParser()		
		cf.read("/data/h2_admin/admin/yunwei/server.conf")
		self.options = cf.options("get_all_server")
		for o in self.options:
			url=cf.get("get_all_server","%s"%o)
			self.down_xml(url,'%s'%o)


	def get_all_plat_info(self):
		#下载所有xml进行解析
		self.down_all_xml()
		bigalls={}
		for o in self.options:
			dic = self.get_info("/tmp/%s.xml"%o)
			bigalls.update(dic)

		return bigalls


	def get_all_plat_ip_port(self):
		bigalls=self.get_all_plat_info()
		allips={}
		for p in bigalls:
			ip=bigalls[p].get("ip")
			port=bigalls[p].get("port")
			dirc={ip:{}}
			dirc[ip].update({"ip":ip,"port":port})
			allips.update(dirc)
		return allips


		#获取所有的 id ip platform
	def get_all_info(self,xmlfile):
		xml=parse_xml(xmlfile,show_log=False)
		#判断文件
		xml.xml_exists()		
		xml.get_root()
		all=[]
		childs=xml.get_element_children(xml.root)
		for child in childs:
			l=[]
			cid=child.get("id")
			ip=child.get("ip")
			plat=child.get("platform")
			l.append(cid)
			l.append(ip)
			l.append(plat)
			all.append(l)
		return all			


		#某台机器中有几个服
		#{'52.76.13.29': 'en_s1,en_s13,en_s7', '52.74.174.169': 'en_s10,en_s15,en_s16'}
	def get_ip_server(self,xmlfile):
		all=self.get_all_info(xmlfile)
		ips=[]
		for l in all:
			ips.append(l[1])
		total_ip=sorted(list(set(ips)))
		ip_server={}
		for ip in total_ip:
			string=""
			for l in all:
				if ip == l[1]:
					server="%s_s%s"%(l[2],l[0])
					string=string+","+server
					string=string.strip(",")
					dirc={ip:string}
					ip_server.update(dirc)
		return ip_server
