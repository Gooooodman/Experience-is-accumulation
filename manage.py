#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="lupuxiao" 
"""
管理入口

功能：
开关游戏
从首服打包文件上传游戏服
reload 代码
执行shell命令
执行erland命令

-t tw_s1,tw_s3~tw_s6  --stop  | --start
-t ALL   --file config,sys --copy --reload   --name 
-t ALL --name qq   --shell_cmd|--erland_cmd

-t ALL --mfile " " --copy 传送所有模板文件
"""
#系统
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
import ConfigParser
import Queue
import time
#本地
from tools.colour import *
from tools.get_server import get_server
from tools.dizun import monitor
from tools.common import split_single

#选项处理
def parser_command():
	usage = """%prog < -t ALL|tw_s1,tw_s3~tw_s7,qq_s1 >  --start|--stop --localfile 本地文件 --despath 远程路径 < --mfile 模板文件|* --copy  --reload > --name  qq|tw|android|yy|ios|i9|vn|tszn  --copy_php   --shell|--erland"""
	parser = OptionParser(usage=usage)		
	parser.add_option("--start",action="store_true",dest="start",help="开启游戏服")
	parser.add_option("--stop",action="store_true",dest="stop",help="关闭游戏服")
	parser.add_option("--reload",action="store_true",dest="reload",help="reload 传过去的文件")
	parser.add_option("--copy",action="store_true",dest="copy",help="从首服打包文件,传送给其他服")
	parser.add_option("--copy_php",action="store_true",dest="copy_php",help="从首服打包php文件,传送给其他机器")
	parser.add_option("--parallel",dest="parallel",type="int",help="可选项,指定并行线程数,默认为8",metavar="num")
	parser.add_option("-t",action="store",type="str",dest="topo",help="指定渠道服如yy_s1,qq_s3,tw_s4或者指定全部ALL",metavar="tw_s1,tw_s3~tw_s8,tw_s11")
	parser.add_option("--mfile",action="store",type="str",dest="file",help="传送模板文件至游戏服  config sys..(如果打包全部 使用--mfile 'all' 参数为all)",metavar="config,sys_money,_http_admin|all")	
	parser.add_option("--localfile",action="store",type="str",dest="localfile",help="传送机器中的文件..如脚本/tmp/1.sh..",metavar="file")
	parser.add_option("--despath",action="store",type="str",dest="despath",help="传送机器中的路径..如/tmp/txt/",metavar="路径")	
	parser.add_option("--name",action="store",type="str",dest="name",help="指定渠道如qq|tw|android|yy|vn|ios|tszn",metavar="指定渠道:en|qq|tw|android|yy|ios|tszn|vn")
	parser.add_option("--shell",action="store",type="str",dest="shell_cmd",help="执行shell命令",metavar="hostname")
	parser.add_option("--erland",action="store",type="str",dest="erland_cmd",help="执行erland命令",metavar="serv_pay_activity:reload_data()")
	parser.add_option("-p","--progress",action="store_true",dest="progress",help="显示运行状态")

	option,args = parser.parse_args()
	if not option.topo:
		parser.error("\033[1;31m选项-t 必须指定\033[0m")
	if option.file:
		if option.shell_cmd or option.erland_cmd:
			parser.error("\033[1;31m选项--file 不能与  --shell  --erland 同时使用\033[0m")
	if option.start or option.stop:
		if option.file or option.copy or option.reload:
			parser.error("\033[1;31m选项--start 与 --stop  不能与 --mfile  --copy --reload 同时使用\033[0m")
	if option.topo == "ALL":
		if not option.name:
			parser.error("\033[1;31m选项-t ALL 必须指定 --name qq|tw|android|yy|vn\033[0m")
	if  option.copy or option.reload:
		if not option.file:
			parser.error("\033[1;31m选项--copy 与 --reload 必须指定 --file \033[0m")
	if option.file:
		if not option.name:
			parser.error("\033[1;31m选项--mfile 必须指定 --name \033[0m")
	if option.localfile and option.despath:
		if option.file:
			parser.error("\033[1;31m选项--localfile --despath 不能与 --mfile 模板文件 同时指定\033[0m")
	if option.localfile:
		if not option.despath:
			parser.error("\033[1;31m选项--localfile (本地文件路径) 与 --despath (目标文件路径) 必须同时指定 \033[0m")
	if option.topo != 'ALL':
		if option.name:
			parser.error("\033[1;31m选项-t 不是ALL 不能与 --name 同时指定\033[0m")

	if option.copy_php:
		if option.localfile or option.file:
			parser.error("\033[1;31m选项--copy_php 不能与 --localfile --mfile  同时指定\033[0m")

	return (option,args)


#agents为字典
def make_topo_queue(agents):
	queue = Queue.Queue(0)
	for agent in agents:
		agentinfo=agents[agent]			
		queue.put(agentinfo)
	return queue

def main(avgr):
	ABSPATH=os.path.abspath(sys.argv[0])
	script_path=os.path.dirname(ABSPATH)
	cf = ConfigParser.ConfigParser()
	cf.read("%s/server.conf"%script_path)
	option,args = parser_command()

	try:
		if option.name:		
			options = cf.options("get_all_server")
			if option.name not in options:
				print "\033[1;31m所指定的 %s 平台不在配置列表(server.conf)中,请核对或者进行添加..\033[0m"%(option.name)
				exit(1)		
			url=cf.get("get_all_server",option.name)
			# if option.name == "android":
			# 	option.name = "ios_yueyu"

			gt=get_server()
			gt.down_xml(url,option.name)
			filename="/tmp/%s.xml"%(option.name)
			gt=get_server()
			all = gt.get_plat_info(filename,option.name)
			if option.parallel:
				parallel = option.parallel
			else:			
				if len(all) > 10:
					parallel = 10
				else:
					parallel = len(all)
			alllist=sorted(all.iteritems(),key=lambda a:int(a[1].get("id")),reverse=False)
			# if option.name == "ios_yueyu":
			# 	server = "s12"
			# else:
			server = "s1"
			
			sshport = int(cf.get("port",option.name))
			if option.topo == "ALL":
				#开始执行--start
				if option.start:
					print "\033[1;33m##########请检查是否开启以下游戏.服数为：%s ##########\033[0m"%(len(alllist))
					for s in alllist:
						print '''\033[1;32m"%s"\033[0m -- %s:%s'''%(s[0],s[1]["ip"],s[1]["port"])
					anwser = ""
					while anwser != "yes":
						anwser = raw_input("警告:执行\033[1;33m开启以上所有游戏\033[0m确认无误后请输入yes,退出请输入no	")
						anwser = anwser.lower()
						if anwser == "no":
							exit(1)
					game=monitor()
					task_queue = make_topo_queue(all)
						#执行开启
					game.start_thread(parallel,task_queue)

					#开始执行--stop
				if option.stop:
					print "\033[1;33m##########请检查是否关闭以下游戏.服数为：%s ##########\033[0m"%(len(alllist))
					for s in alllist:
						print '''\033[1;32m"%s"\033[0m -- %s:%s'''%(s[0],s[1]["ip"],s[1]["port"])
					anwser = ""
					while anwser != "yes":
						anwser = raw_input("警告:执行\033[1;33m关闭以上所有游戏\033[0m确认无误后请输入yes,退出请输入no	")
						anwser = anwser.lower()
						if anwser == "no":
							exit(1)

					game=monitor()
					task_queue = make_topo_queue(all)
						#执行关闭
					game.stop_thread(parallel,task_queue)	

				#传送模板文件
				if option.file:		
					host=cf.get("start_ip",option.name)

					plat="%s_%s"%(option.name,server)
					if option.file == "all":
						filelist=[]
					else:	
						filelist=option.file.split(",")
					destar="server.tar.gz"
					game=monitor()
					#打包首服的文件并下载到/tmp
					print '''\033[1;32m"%s"\033[0m开始执行从 %s 打包下载操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),plat)
					game.tar_file(filelist,option.name,server,host,destar,sshport)

					if plat in all:
						all.pop(plat)
						if len(all) == 0:
							print '''\033[1;32m"success",排除首服.没有服可以更新模板文件了.程序退出\033[0m'''	
							exit(0)							
					else:
						print '''\033[1;31m首服"%s" 不在 %s 中停止执行...\033[0m'''%(plat,all)	
						exit()	

					#copy 从本地/tmp把文件传至其它服
					if option.copy:
						tarfile="/tmp/server.tar.gz"
						print "\033[1;33m##########请检查是否拷贝文件至以下游戏.服数为：%s ##########\033[0m"%(len(alllist))
						for s in alllist:
							print '''\033[1;32m"%s"\033[0m -- %s:%s'''%(s[0],s[1]["ip"],s[1]["port"])
						anwser = ""
						while anwser != "yes":
							anwser = raw_input("警告:执行\033[1;33m拷贝文件至以上所有游戏\033[0m确认无误后请输入yes,退出请输入no	")
							anwser = anwser.lower()
							if anwser == "no":
								exit(1)
								#上传到每个服
						print '''\033[1;32m"%s"\033[0m开始执行上传操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()))
						game=monitor()
						task_queue = make_topo_queue(all)
						game.uploadtar_to_server_thread(parallel,task_queue,tarfile)
						#每个服解压
						print '''\033[1;32m"%s"\033[0m开始执行解压操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()))
						game=monitor()
						task_queue = make_topo_queue(all)
						game.decompression_file_thread(parallel,task_queue,destar)

					#reload file
					#reload 模板代码
					if option.reload:
						print '''\033[1;32m"%s"\033[0m开始执行reload操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()))
						game=monitor()
						task_queue = make_topo_queue(all)
						game.reload_server_thread(parallel,task_queue,filelist)						
				#执行--shell 命令
				if option.shell_cmd:	
					print '''\033[1;32m"%s"\033[0m开始执行shell命令： %s 操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),option.shell_cmd)
					warn_cmd = ["halt","rm","reboot","rm /","rm *",'rm -rf /*','rm -f *','shutdown']
					if option.shell_cmd in warn_cmd:
						print '''\033[1;31m"warning",不能执行 %s 操作.\033[0m'''%(option.shell_cmd)
						exit(1)
					plat="%s_%s"%(option.name,server)
					if plat in all:
						all.pop(plat)
						if len(all) == 0:
							print '''\033[1;32m"success",排除首服.没有服可以执行shell命令了.程序退出\033[0m'''	
							exit(0)							
					else:
						print '''\033[1;31m首服"%s" 不在 %s 中停止执行...\033[0m'''%(plat,all)	
						exit()				
					game=monitor()
					task_queue = make_topo_queue(all)
					game.run_cmd_thead(parallel,task_queue,option.shell_cmd,option.progress)
					#执行erland命令 --erlang
				if option.erland_cmd:
					erland_cmd = """./gamectl eval '%s'"""%option.erland_cmd
					print '''\033[1;32m"%s"\033[0m开始执行erland命令：%s 操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),option.erland_cmd)
					plat="%s_%s"%(option.name,server)
					if plat in all:
						all.pop(plat)
						if len(all) == 0:
							print '''\033[1;32m"success",排除首服.没有服可以执行erlang命令了.程序退出\033[0m'''		
							exit(0)							
					else:
						print '''\033[1;31m首服"%s" 不在 %s 中停止执行...\033[0m'''%(plat,all)	
						exit()
					game=monitor()
					task_queue = make_topo_queue(all)
					game.run_cmd_thead(parallel,task_queue,erland_cmd)

				#--localfile 本地文件  --despath 远程机器路径
				if option.localfile and option.despath:
					print '''\033[1;32m"%s"\033[0m开始执行向%s所有主机传送文件操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),option.name)
					gt=get_server()
					ips=gt.get_plat_ip_port("/tmp/%s.xml"%option.name,option.name)
					host=cf.get("start_ip",option.name)
					if option.parallel:
						parallel = option.parallel
					else:												
						if len(ips) > 10:
							parallel = 10
						else:
							parallel = len(ips)
					if host in ips:
						ips.pop(host)
						if len(ips) == 0:
							print '''\033[1;32m"success",没有ip可以更新php了.程序退出\033[0m'''	
							exit(0)							
					else:
						print '''\033[1;31m"fail","%s"首服IP: %s 不在 %s 中,请查看...\033[0m'''%(option.name,host,ips)
					game=monitor()
					task_queue = make_topo_queue(ips)
					game.send_file_thread(parallel,task_queue,option.localfile,option.despath)		

				#传送php文件至远程机器
				if option.copy_php:
					print '''\033[1;32m"%s"\033[0m开始执行从%s_%s打包下载php文件向操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),option.name,server)
					gt=get_server()
					ips=gt.get_plat_ip_port("/tmp/%s.xml"%option.name,option.name)
					host=cf.get("start_ip",option.name)
					if host in ips:
						ips.pop(host)
						if len(ips) == 0:
							print '''\033[1;32m"success",没有ip可以更新php了.程序退出\033[0m'''	
							exit(0)								
					else:
						print '''\033[1;31m"fail","%s"首服IP: %s 不在 %s 中,请查看...\033[0m'''%(option.name,host,ips)
						exit(1)
					if option.parallel:
						parallel = option.parallel
					else:												
						if len(ips) > 10:
							parallel = 10
						else:
							parallel = len(ips)						
					#打包首服php 并下载在本地/tmp
					game=monitor()
					game.tar_down_php(host=host,sshport=sshport)

					print '''\033[1;32m"%s"\033[0m开始执行向%s所有主机传送php文件操作...'''%(time.strftime("%Y-%m-%d %X", time.localtime()),option.name)				
					task_queue = make_topo_queue(ips)	
					#从本地上传到远程机器
					game.send_php_tar_thread(parallel,task_queue,file='/tmp/php.tar.gz',desfile='php.tar.gz')						



		else:
			servers=option.topo 
			serverslist1=split_single(servers)
			serverslist=[]
			for single in serverslist1:
				serverslist.append(single)
			gt=get_server()
			bigdic=gt.get_all_plat_info()
			rmovelist=[]
			newdic={}
			for s in serverslist:
				if s not in bigdic:
					rmovelist.append(s)
				else:
				 	dirc={s:{}}
				 	dirc[s].update(bigdic[s])
					newdic.update(dirc)
			if rmovelist :		
				print "\n\033[1;33m%s\033[0m 已被合服,停止执行...\n"%rmovelist
			alllist=sorted(newdic.iteritems(),key=lambda a:int(a[1].get("id")),reverse=False)
			if option.parallel:
				parallel = option.parallel
			else:				
				if len(newdic) > 10:
					parallel = 10
				else:
					parallel = len(newdic)					
			if option.start:
				print "\033[1;33m##########请检查是否开启以下游戏.服数为：%s ##########\033[0m"%(len(alllist))
				for s in alllist:
					print '''\033[1;32m"%s"\033[0m -- %s:%s'''%(s[0],s[1]["ip"],s[1]["port"])
				anwser = ""
				while anwser != "yes":
					anwser = raw_input("警告:执行\033[1;33m开启以上所有游戏\033[0m确认无误后请输入yes,退出请输入no	")
					anwser = anwser.lower()
					if anwser == "no":
						exit(1)
				game=monitor()
				task_queue = make_topo_queue(newdic)
					#执行开启
				game.start_thread(parallel,task_queue)
			if option.stop:
				print "\033[1;33m##########请检查是否关闭以下游戏.服数为：%s ##########\033[0m"%(len(alllist))
				for s in alllist:
					print '''\033[1;32m"%s"\033[0m -- %s:%s'''%(s[0],s[1]["ip"],s[1]["port"])
				anwser = ""
				while anwser != "yes":
					anwser = raw_input("警告:执行\033[1;33m关闭以上所有游戏\033[0m确认无误后请输入yes,退出请输入no	")
					anwser = anwser.lower()
					if anwser == "no":
						exit(1)
				game=monitor()
				task_queue = make_topo_queue(newdic)
					#执行开启
				game.stop_thread(parallel,task_queue)			

	except KeyboardInterrupt:
		warn("程序被强行停止!!")   







if __name__ == "__main__":
	main(sys.argv)









































