#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="lupuxiao" 

'''dizun游戏开关 文件操作类'''

import Queue
import subprocess
import time
import re,sys
from ssh import ssh
import Queue
from parallel import ThreadQueue
from common import Progress


class monitor():
	def __init__(self,waittime=1,config_dir="/data/server",option="-o StrictHostKeyChecking=no -o GSSAPIAuthentication=no",identify=None):
		self.waittime = waittime
		self.option=option
		self.config_dir=config_dir
		self.identify = identify

#得到渠道版本号
	def get_plat_version(self,host,sshport,plat,server="s1"):
		get_version='''grep "code" /data/server/%s_%s/log/version.txt'''%(plat,server)
		try:
			SSH = ssh(host=host,port=sshport)
			stdout,stderr,returncode = SSH.run(get_version,drop_socket=False)
			if returncode != 0:raise Exception(stderr)
			output = stdout.strip("\n")	
			#print output
		except Exception,err:
			raise Exception(err)
		return output
		
	
	def get_pid_query(self,plat,server,host,sshport):
		cmd_query='''pgrep -f %s_%s/config||echo "0"'''%(plat,server)
		try:
			SSH = ssh(host=host,port=sshport)			
			stdout,stderr,returncode = SSH.run(cmd_query,drop_socket=False)
			if returncode != 0:raise Exception(stderr)
			output = stdout.strip("\n")	
			#print output
		except Exception,err:
			raise Exception(err)
		return output		

	def status(self,plat,server,host,sshport):
		output=self.get_pid_query(plat,server,host,sshport)
		#print output
		if output == "0":
			message = "\033[1;33m%s_%s\033[0m 处于关闭中...主机[%s] .."%(plat,server,host)
			running = "false"
		else:
			message = "\033[1;32m%s_%s\033[0m运行在进程id:%s"%(plat,server,output)
			running = "true"
		#print message,running
		return message,running


	def start(self,plat,server,host,sshport):
		try:
			message,running = self.status(plat,server,host,sshport)
		except Exception,err:
			MESSAGE = '''\033[1;31m获取"%s_%s" 状态失败,ip:%s,错误信息:{%s}'''%(plat,server,host,err)
			raise Exception(MESSAGE)

		if running == "true":
			MASSAGE = '''\033[1;33m"warning","%s_%s" 目前状态:开启 执行动作:开启 执行结果:无需开启操作\033[0m'''% (plat,server)
			print MASSAGE			
		if running == "false":
			#start_cmd= "bash /data/server/%s_%s/gamectl start"%(plat,server)
			start_cmd= '''"cd /data/server/%s_%s/ && ./gamectl start"'''%(plat,server)
			try:
				SSH=ssh(host=host,port=sshport)
				for r in range(1,4):
					stdout,stderr,returncode = SSH.run(start_cmd,drop_socket=False)					
					time.sleep(self.waittime)
					message,running = self.status(plat,server,host,sshport)
					if running == "true":
						MESSAGE = '\033[1;32m"success",%s_%s 目前状态:关闭 执行动作:开启 执行结果:开启%d次成功\033[0m'%(plat,server,r)
						print MESSAGE
						break
					else:									
						if r < 3:
							print "\033[1;33m%s_%s 经过%d次还在开启中....\033[0m"%(plat,server,r)
							continue
						if r == 3:
							print "\033[1;31m%s_%s 经过%d次开启失败....失败信息:{%s,%s}\033[0m"%(plat,server,r,stderr,stdout)
							break
			except Exception,err2:
				MASSAGE = '''\033[1;31m "%s_%s" 执行开启动作失败,ip:%s,错误信息:{%s}\033[0m'''%(plat,server,host,err2)
				raise Exception(MESSAGE)	

	#上传文件到机器中
	def send_file(self,host,sshport,file,desfile):
		SSH=ssh(host=host,port=sshport)
		stdout,stderr,KB,code=SSH.sendfile(source=file,dest=desfile,drop_socket=False)
		if code != 0:
			message = '''\033[1;31m"fail",传送 %s 到 %s:%s 失败..信息：%s,%s\033[0m'''%(file,host,desfile,stdout,stderr)
			raise Exception(message)	
		print '''\033[1;32m"success",传送 %s 到 %s:%s 成功\033[0m'''%(file,host,desfile)

		#传送php.tar.gz
	def send_php_tar(self,host,sshport,file="/tmp/php.tar.gz",desfile="php.tar.gz"):
		PHP_SRC_CODE_DIR="/data/web/mwygz/admin"
		despath="%s/%s"%(PHP_SRC_CODE_DIR,desfile)	
		#上传php.tar.gz
		self.send_file(host,sshport,file,PHP_SRC_CODE_DIR)
		
		#解压
		tar_cmd = '''"cd %s && tar xzf %s && chown -R apache:apache ."'''%(PHP_SRC_CODE_DIR,desfile)
		SSH=ssh(host=host,port=sshport)
		stdout,stderr,returncode=SSH.run(tar_cmd,drop_socket=False)
		message = "\033[1;31m'fail','%s'执行'%s'出错,信息:%s|%s\033[0m"%(host,tar_cmd,stdout,stderr)
		if returncode != 0:raise Exception(message)
		print '\033[1;32m"success"在"%s"上解压"%s"成功..\033[0m'%(host,despath)		

		#从首服下载php代码并下载到本地/tmp
	def tar_down_php(self,host,sshport,downpath="/tmp"):
		PHP_SRC_CODE_DIR="/data/web/mwygz/admin"
		CODE_TAR="php.tar.gz"
		TMP_FROM="/data/web/mwygz/admin/php.tar.gz"
		#从服务器上打包
		cmd = '''"cd %s && /bin/tar zcf %s --exclude=protected/config/config.php --exclude=protected/template_c/* --exclude=protected/config/servers/*  public  protected  log"'''%(PHP_SRC_CODE_DIR,CODE_TAR)
		SSH=ssh(host=host,port=sshport)
		stdout,stderr,returncode=SSH.run(cmd,drop_socket=False)
		if returncode != 0:
			message = '\033[1;31m"fail","%s:%s"cmd:"%s" 失败...\033[0m'%(host,port,cmd)
			raise Exception(message)
		print '''\033[1;32m"success","%s:%s" 路径:"%s"打包文件成功...\033[0m'''%(host,sshport,TMP_FROM)	

		#下载
		down_cmd="scp -C -r %s -P %s root@%s:%s  %s"%(self.option,sshport,host,TMP_FROM,downpath)
		ret=subprocess.Popen(down_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		stdout,stderr = ret.communicate()
		if ret.returncode != 0:
			message = '\033[1;31m"fail","%s:%s"下载"%s"到本地"%s"失败,信息: %s|%s \033[0m'%(host,sshport,TMP_FROM,downpath)
			raise Exception(message)
		print '''\033[1;32m"success","%s:%s","%s"下载"%s"成功..\033[0m'''%(host,sshport,TMP_FROM,downpath)


	#上传到游戏服server.tar.gz
	def uploadtar_to_server(self,tarfile,plat,server,host,sshport):
		path="%s/%s_%s/"%(self.config_dir,plat,server)
		cmd = """scp -C -r  %s -P %s %s root@%s:%s"""%(self.option,sshport,tarfile,host,path)
		try:
			for i in range(1,4):
				ret=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
				while ret.poll() == None:
					Progress(info="%s_%s正在传送中..."%(plat,server),sleep=0.7)
				stdout,stderr = ret.communicate()
				out = stderr.strip("\n")
				if ret.returncode != 0:
					time_out = re.compile("Connection timed out")
					if time_out.findall(out):
						continue
					if i == 3:
						print  '''\033[1;31m"fail",%s_%s第%s次上传失败.%s\033[0m'''%(plat,server,i,stderr.strip("\n"))
						exit(2)												
				else:
					break
			print '''\033[1;32m"success","%s_%s"上传成功...\033[0m'''%(plat,server)
		except Exception,err:
			raise Exception(err)


	#解压游戏服/data/server/tw_s1/server.tar.gz
	def decompression_file(self,plat,server,host,desfile,sshport):
		cmd = '''"cd /data/server/%s_%s/ && tar xzf %s"'''%(plat,server,desfile)
		try:			
			SSH=ssh(host,port=sshport)
			stdout,stderr,returncode=SSH.run(cmd,drop_socket=False)
			if returncode != 0:
				print '''\033[1;31m"%s_%s"在%s上解压%s失败\033[0m,失败信息：{%s,%s}'''%(plat,server,host,desfile,stdout,stderr)
				exit()
			print '''\033[1;32m"success","%s_%s"解压%s成功...\033[0m'''%(plat,server,desfile)
		except Exception,err:
			message = '''"decompression_file 解压函数执行失败...信息{%s}"'''%err 
			raise Exception(message)



		#打包config,beam
	def tar_file(self,filelist,plat,server,host,destar,sshport):
		if len(filelist) == 0:
			fstring="所有文件"
			cmd = '''"cd /data/server/%s_%s/ && tar czf %s --exclude=sql/backup/* --exclude=sql/recover/* sql script gamectl user_default.beam ebin config/game.crontab "'''%(plat,server,destar)
		else:
			fstring=""
			for f in filelist:
				if f == "config":
					fstring=fstring+"config/common.conf "
				else:
					fstring=fstring+"ebin/*/%s.beam "%f 
			print "\033[1;33m所需打包的文件:\033[0m",fstring
			cmd = '''"cd /data/server/%s_%s/ && tar czf %s --exclude=sql/backup/* --exclude=sql/recover/* %s"'''%(plat,server,destar,fstring)
		tarfile="/data/server/%s_%s/%s"%(plat,server,destar)
		local_cmd = '''scp -C -r -P %s root@%s:%s /tmp/'''%(sshport,host,tarfile)

		try:
			SSH=ssh(host,port=sshport)
			#print '''\033[1;32m"%s_%s"\033[0m,%s打包...CMD:\033[1;33m%s\033[0m'''%(plat,server,host,cmd)
			stdout,stderr,returncode=SSH.run(cmd,drop_socket=False)
			if returncode != 0:
				message = '''\033[1;31m在"%s_%s"主机%s上打包"%s"失败,失败信息:{%s,%s}\033[0m'''%(plat,server,host,fstring,stdout,stderr)
				raise Exception(message)
			print '''\033[1;32m在"%s_%s"主机%s上打包"%s"成功...\033[0m'''%(plat,server,host,fstring)
			#下载到本地
			print '''\033[1;32m开始下载%s文件在/tmp 下\033[0m'''%(tarfile)
			ret = subprocess.Popen(local_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
			stdout,stderr = ret.communicate()
			if ret.returncode != 0:
				print "\033[1;31m从%s '%s_%s'下载 %s 失败.失败信息:%s,%s\033[0m"%(host,plat,server,tarfile,stdout,stderr)
				exit()		
		except Exception,err:
			message = '''"tar_file 打包函数执行失败...信息{%s}"'''%err 
			raise Exception(message)


	def stop(self,plat,server,host,sshport):
		try:
			message,running = self.status(plat,server,host,sshport)
		except Exception,err:
			MASSAGE = '''\033[1;31m获取"%s_%s" 状态失败,ip:%s,错误信息:{%s}'''%(plat,server,host,err)
			raise Exception(MASSAGE)
		if running == "false":
			MASSAGE = '''\033[1;33m"warning","%s_%s" 目前状态:关闭 执行动作:关闭 执行结果:无需关闭操作\033[0m'''% (plat,server)
			print MASSAGE
		if running == "true":
			#stop_cmd = "bash /data/server/%s_%s/gamectl sync_stop -q"%(plat,server)
			stop_cmd = '''"cd /data/server/%s_%s/ && ./gamectl sync_stop -q"'''%(plat,server)
			try:
				SSH=ssh(host=host,port=sshport)
				for r in range(1,4):
					stdout,stderr,returncode = SSH.run(stop_cmd,drop_socket=False)
					time.sleep(self.waittime)
					message,running = self.status(plat,server,host,sshport)
					if running == "false":
						MASSAGE = '\033[1;32m"success",%s_%s 目前状态:开启 执行动作:关闭 执行结果:关闭%d次成功\033[0m'%(plat,server,r)
						print MASSAGE
						break
					if running == "true":
						if r < 3:
							print "\033[1;33m%s_%s 经过%d次还在关闭中....\033[0m"%(plat,server,r)
							continue	
						if r == 3:
							print "\033[1;31m%s_%s 经过%d次关闭失败....失败信息:{%s,%s}\033[0m"%(plat,server,r,stderr,stdout)
							break								
			except Exception,err2:
				MASSAGE = '''\033[1;31m "%s_%s" 执行关闭动作失败,ip:%s,错误信息:{%s}\033[0m'''%(plat,server,host,err2)
				raise Exception(MESSAGE)

			
	def run_cmd(self,plat,server,host,sshport,scmd,progress=False):
		shell_com='''"cd %s/%s_%s/ && %s"'''%(self.config_dir,plat,server,scmd)
		#print "开始 %s_%s "%(plat,server)
		try:
			SSH=ssh(host,port=sshport,progress=progress)
			stdout,stderr,returncode=SSH.run(shell_com,drop_socket=False)
			if returncode != 0:
				print '''\033[1;31m"%s_%s"在%s上执行cmd:%s失败\033[0m,失败信息：%s,%s'''%(plat,server,host,scmd,stderr,stdout)
				exit()
			print '''\033[1;32m"success","%s_%s"上执行 %s 成功...\033[0m.结果：%s'''%(plat,server,scmd,stdout.strip("\n"))
		except Exception,err:
			message = '''"shell_cmd 执行命令函数执行失败...信息{%s}"'''%err 
			raise Exception(message)			



	#reload sys_money sys_physical_activity config
	def reload_server(self,plat,server,host,filelist,sshport):
		rlist=filelist
		fstring=""
		SSH=ssh(host,port=sshport)
		config=False
		mfiles=False
		if "config" in filelist:
			config = True
		else:
			mfiles = True
		if config:
			reload_conf = '''"cd %s/%s_%s/ &&./gamectl reload -r config"'''%(self.config_dir,plat,server)
			stdout,stderr,returncode = SSH.run(reload_conf,drop_socket=False)
			if returncode != 0:
				message = '''\033[1;31m"%s_%s reload config "失败..IP:%s 信息：{%s}\033[0m'''%(plat,server,host,stderr.strip("\n"))
				raise Exception(message)
			print '''\033[1;32m"success",%s_%s reload conf  \033[0m'''%(plat,server)					
		if mfiles:
			for i in filelist:
				fstring=fstring+" "+i
			reload_file = '''"cd %s/%s_%s/ &&./gamectl reload -r code  '%s'"'''%(self.config_dir,plat,server,fstring)
			stdout1,stderr1,returncode = SSH.run(reload_file,drop_socket=False)
			if returncode != 0:
				message = '''\033[1;31m"fail","%s_%s" CMD: %s \033[0m 错误信息："%s,%s"'''%(plat,server,reload_file,stdout1.strip("\n"),stderr1.strip("\n"))
				print message
			else:		
				print '''\033[1;32m"success",%s_%s reload files:%s\033[0m'''%(plat,server,fstring)	

		
			#启多线程 reload 
	def reload_server_thread(self,parallel,task_queue,filelists):
		if "config" in filelists:
			if len(filelists) != 1:
				print '\033[1;33m"warning",config在模板中,只更新config,其它模板请在次一起更新\033[0m'
		def reloads(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.reload_server(plat,server,host,filelists,sshport)
				except Exception,err:
					message = '\033[1;31m"fail","%s_%s"reload出错,出错信息: %s\033[0m' % (plat,server,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(reloads,parallel,task_queue)

	def send_php_tar_thread(self,parallel,task_queue,file='/tmp/php.tar.gz',desfile='php.tar.gz'):
		def send_php(task_queue):
			while True:
				agent=task_queue.get()
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.send_php_tar(host,sshport,file,desfile)
				except Exception,err:
					message = '\033[1;31m"fail","send_php_tar_thread","%s:%s"出错,出错信息:%s"\033[0m' % (host,sshport,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(send_php,parallel,task_queue)							

	def run_cmd_thead(self,parallel,task_queue,scmd,progress=False): 
		def cmd(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.run_cmd(plat,server,host,sshport,scmd,progress=progress)
				except Exception,err:
					message = '\033[1;31m"fail","cmd %s_%s出错,出错信息:%s"\033[0m' % (plat,server,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(cmd,parallel,task_queue)								


	def send_file_thread(self,parallel,task_queue,file,desfile):
		def send(task_queue):
			while True:
				info=task_queue.get()
				host=info.get("ip")
				sshport=info.get("port")
				try:
					self.send_file(host,sshport,file,desfile)
				except Exception,err:
					message = '\033[1;31m"fail",send_file_thread %s:%s  %s  %s 出错信息：%s \033[0m'%(host,sshport,file,desfile,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(send,parallel,task_queue)



	def start_thread(self,parallel,task_queue):
		def start(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.start(plat,server,host,sshport)
				except Exception,err:
					message = '\033[1;31m"fail","关闭%s_%s出错,出错信息:%s"\033[0m' % (plat,server,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(start,parallel,task_queue)

	def status_thread(self,parallel,task_queue):
		def stat(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					mess,pid=self.status(plat,server,host,sshport)
					print mess
				except Exception,err:
					message = '\033[1;31m"fail","状态%s_%s出错,出错信息:%s"\033[0m' % (plat,server,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(stat,parallel,task_queue)				



	def stop_thread(self,parallel,task_queue):
		def stop(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.stop(plat,server,host,sshport)
				except Exception,err:
					message = '\033[1;31m"fail","开启%s_%s出错,出错信息:%s"\033[0m' % (plat,server,err)
					print message
				finally:
					task_queue.task_done()
		ThreadQueue(stop,parallel,task_queue)		



			##上传server.tar.gz
	def uploadtar_to_server_thread(self,parallel,task_queue,tarfile):
		def upload(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.uploadtar_to_server(tarfile,plat,server,host,sshport)
				except Exception,err:
					message = '\033[1;31m"fail","上传文件%s到%s_%s出错,出错信息:%s"\033[0m' % (tarfile,plat,server,err)
					print message
				finally:
					task_queue.task_done()									
		ThreadQueue(upload,parallel,task_queue)		


			#解压server.tar.gz
	def decompression_file_thread(self,parallel,task_queue,desfile):
		def decomper(task_queue):
			while True:
				agent=task_queue.get()
				plat=agent.get("platform")
				server="s%s"%(agent.get("id"))
				host=agent.get("ip")
				sshport=agent.get("port")
				try:
					self.decompression_file(plat,server,host,desfile,sshport)
				except Exception,err:
					message = '\033[1;31m"fail","在%s_%s %s 解压%s出错,出错信息:%s"\033[0m' % (plat,server,host,tarfile,err)
					print message
				finally:
					task_queue.task_done()									
		ThreadQueue(decomper,parallel,task_queue)										



if __name__ == "__main__":
	pass
	# game=monitor()
	# # # plat="tw"
	# # # server="s7"
	# # # host="119.29.87.125"
	# # # sshport=10022
	# # # file="/tmp/ips.txt"
	# # # desfile="/tmp/txt/"
	# # # game.send_file(host,sshport,file,desfile)
	# # # mess,running=game.status(plat,server,host)
	# # # print mess
	# # #game.reload_server(plat,server,host,filelist)
	# # #查看状态
	# # #mess,run=game.status(plat,server,host)
	# # #print mess,run
	# # #关闭
	# # #game.stop(plat,server,host)
	# # #开启
	# # #game.start(plat,server,host)
	# # #reload
	# filelist=['mod_pay']
	# # # #game.reload_server(plat,server,host,filelist)

	# # #测试线程
	# # #stop
	# parallel=1
	# # # # def make_topo_queue(lists):
	# # # # 	queue = Queue.Queue(0)
	# # # # 	for list in lists:
	# # # # 		queue.put(list.rstrip())
	# # # # 	return queue
	# # # #agents={"119.29.87.125":{"ip":"119.29.87.125",'port':10022}}

	# # # #{'yy_s18': {'id': '18', 'ip': '120.132.72.34', 'port': 10022, 'platform': 'yy'}
	# # # #agents={'dev_s998':{"platform": "dev","id": "998","ip": "120.132.77.182",'port': 10022}}
	# # # #agents = {"dev_s998":{"ip":"120.132.77.182",'port':10022,'platform':'dev','id':'998'}}
	# agents={"qq_s98":{"ip": "119.29.58.99",'port': 10022,'platform': 'qq',"id": "98"}}
	# # # # task_queue = Queue.Queue(0)
	# # agents={"119.29.16.251":{"ip": "119.29.16.251",'port': 10022},"119.29.114.245":{"ip": "119.29.114.254",'port': 10022}}
	# def make_topo_queue(agents):
	# 	queue = Queue.Queue(0)
	# 	for agent in agents:
	# 		agentinfo=agents[agent]			
	# 		queue.put(agentinfo)
	# 	return queue
	# task_queue = make_topo_queue(agents)
	# # # #task_queue = make_topo_queue(agents)
	# # # # game.send_file_thread(parallel,task_queue,file,desfile)
	# # # # scmd = "ifconfig"
	# # # # game.run_cmd_thead(parallel,task_queue,scmd)
	# # # # game.stop_thread(parallel,task_queue)
	# # # #task_queue = make_topo_queue(agents)
	# # # #game.start_thread(parallel,task_queue)
	# game.reload_server_thread(parallel,task_queue,filelist)
	# #game.tar_down_php(host="123.59.15.71",sshport=10022)
	# #game.send_php_tar_thread
	# #agents={"123.59.11.108":{"ip": "123.59.11.108",'port': 10022},"123.59.11.186":{"ip": "123.59.11.186",'port': 10022}}
	# #game.send_php_tar_thread(parallel,task_queue,file='/tmp/php.tar.gz',desfile='php.tar.gz')




































