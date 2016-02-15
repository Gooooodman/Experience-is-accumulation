#!/usr/bin/python
# -*- coding: utf-8 -*-
#author yyr lupuxiao 
'''ssh 操作模块

SSH的操作,到远程执行命令'''
import os
import re
import subprocess
import syslog
from common import Progress

class ssh ():
	def __init__(self,host,user="root",identify=None,timeout=6,port=22,option=" -o StrictHostKeyChecking=no -o GSSAPIAuthentication=no",progress=False):
		self.host = host
		self.user = user
		self.identify = identify
		self.port = port
		self.timeout = timeout
		self.option=option
		self.progress =progress

	def ssh_socket(self):		
                '''创建ssh socket 以及后端开启ssh 连接,实现ssh 连接重用'''

                #判断ssh socket是否存在
		cmd = '''ssh -p %d  %s -o ControlPath=~/.ssh/ssh_%%h_%%p.sock -O check %s@%s''' % \
		(self.port,self.option,self.user,self.host)
		cmd_create = ["ssh","-p",str(self.port),"-o","StrictHostKeyChecking=no",
		"-o","ControlMaster=auto","-o","GSSAPIAuthentication=no","-o","ControlPath=~/.ssh/ssh_%h_%p.sock","-o","ControlPersist=yes","-l",self.user,self.host,"exit 0"]		

		if self.identify:
			cmd_create.insert(1,"-i")
			cmd_create.insert(2,self.identify)
		if self.timeout:
			cmd_create.insert(1,"-o")
			cmd_create.insert(2,"ConnectTimeout=%s" % self.timeout)
		#print "ssh_socket --->",cmd	
		run = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		stdout,stderr = run.communicate()
		if run.returncode != 0:
			if "Connection refused" in stderr:
				message = '%s ssh_socket已经失效,重建ssh shocket' % self.host
				#print message
				syslog.syslog(syslog.LOG_WARNING,message)
				os.popen('find ~/.ssh -name "*%s*.sock" -exec rm -f {} \;' % self.host)
				os.popen('pid=`pgrep -f "ssh .+ %s"`;[ -n "$pid" ] && kill $pid' % (self.host))
			try:				
				result = subprocess.check_call(cmd_create)
			except Exception,err:
				message = '\033[1;33m"warning"\033[0m,"%s创建ssh socket失败,直接用直连,错误信息:%s"' % (self.host,err)
				#print message
				syslog.syslog(syslog.LOG_WARNING,message)
			
			#time.sleep(2)

	def run(self,cmd,forwarding=False,drop_socket=True):

		'''通过SSH远程执行命令,并返回标准输出,标准错误,返回执行码,drop_socket默认为True表示完成命令后删除SSH SOCKET'''
		#创建socket
		#if not os.path.exists("/%s/.ssh/ssh_%s_%s.sock"%(self.user,self.host,self.port)):
		self.ssh_socket()
		forward = ""		
		timeout = ""
		if forwarding == True:
			forward = "-A"
		if self.timeout:
			timeout = "-o ConnectTimeout=%s" % self.timeout
		cmdrun = r"""ssh %s %s -o ControlPath=~/.ssh/ssh_%s_%d.sock -l %s   %s -p %s %s %s""" % (forward,timeout,self.host,self.port,self.user,self.option,self.port,self.host,cmd)
		#加入cmd日志记录在/tmp/cmd_时间.log文件
		import time
		cmd_time=time.strftime("%Y-%m-%d %H:%M:%S" , time.localtime())
		hour_time=time.strftime("%Y-%m-%d_%H", time.localtime())
		cmd_log="/tmp/cmd_%s.log"%hour_time
		file=open(cmd_log,'a')
		file.write("[ %s | %s ],%s"%(cmd_time,time.time(),cmdrun))
		file.write("\n")
		file.close()
		###########################
		try:
			run = subprocess.Popen(cmdrun,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
			if self.progress:
				while run.poll() == None:
					Progress(sleep=0.7)
			stdout,stderr = run.communicate()
			outerr=stderr.strip("\n")
			if run.returncode != 0:
				time_out = re.compile("timed out")
				if time_out.findall(outerr):
					for i in range(3):
						print '"warning",第%s次执行中..'%(i+1)
						cmdrun = r"""ssh %s %s  -l %s  %s -p %s %s %s""" % (forward,timeout,self.user,self.option,self.port,self.host,cmd)
						run = subprocess.Popen(cmdrun,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
						if self.progress:
							while run.poll() == None:
								Progress(sleep=0.7)
						stdout,stderr = run.communicate()
						outerr=stderr.strip("\n")
						if run.returncode == 0:
							return stdout,outerr,run.returncode
						if i == 2:
							return stdout,outerr,run.returncode
		except Exception,err:
			raise Exception(err)
		if drop_socket:
			subprocess.call(["ssh","-p",str(self.port),"-o","ControlPath=~/.ssh/ssh_%s_%d.sock"%(self.host,self.port),"-O","exit",self.host])
		return stdout,outerr,run.returncode

	def sendfile(self,source,dest,exclude=None,exclude_from=None,include=None,include_from=None,delete=False,bwlimit=0,ModifyTime=None,prune_empty_dirs=None,drop_socket=True):
		'''通过SSH连接调用rsync传送文件和文件夹

		exclude:排除文件,exclude_from:从文件中获取排除的文件,delete:是否使用rsync的delete参数 ,bwlimit:指定传输带宽(单位KB,0表示不限制),
		ModifyTime:忽略时间单位秒,drop_socket:是否清除SSH SOCKET'''
		host = self.host
		port = self.port
		#创建ssh socket
		self.ssh_socket()
		#判断传送源是否存在
		if not os.path.exists(source):
			message='"fail","directory %s is not exist"' % source
			print message		
			raise Exception(message)
		#如果目标服上面没有传送的父目录则创建
		dir_dest = os.path.dirname(dest.rstrip("/"))
		basename_dest = os.path.basename(dest.rstrip("/"))
		dir = os.path.dirname(source.rstrip("/"))
		basename = os.path.basename(source.rstrip("/"))
		exclude_opt = ""
		exclude_from_opt = ""
		include_opt = ""
		include_from_opt = ""
		delete_rsync = ""
		modify_window = ""
		prune_empty_dirs_opt = ""
		timeout = ""
		if exclude:exclude_opt = "--exclude %s" % exclude
		if exclude_from:exclude_from_opt = "--exclude-from %s" % exclude_from
		if include:include_opt = "--include %s" % include
		if include_from:include_from_opt = "--include-from %s" % include_from
		if delete:delete_rsync = "--delete"
		if ModifyTime:modify_window = "--modify-window=%d" % ModifyTime
		if prune_empty_dirs:prune_empty_dirs_opt = "--prune-empty-dirs"
		if self.timeout:timeout = "-o ConnectTimeout=%s" % self.timeout
		parameter = {"source":source,"dest":dest,"host":host,"port":port,"dir_dest":dir_dest,\
		"basename_dest":basename_dest,"dir":dir,"basename":basename,"bwlimit":bwlimit,"modify_window":modify_window,"timeout":timeout}

		try:
			cmd = """ssh %(timeout)s -p %(port)d -o StrictHostKeyChecking=no -o ControlPath=~/.ssh/ssh_%(host)s_%(port)d.sock -o GSSAPIAuthentication=no %(host)s '[ ! -d %(dest)s ] && mkdir -p %(dest)s || echo "ok"'""" % parameter
			#print cmd
			p = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
			p.communicate()
			if p.returncode != 0:
				raise Exception("创建目录失败....%s"%cmd)
			if os.path.isfile(source):
				sendcmd="/usr/bin/rsync -avzc --rsync-path=/usr/bin/rsync --bwlimit %(bwlimit)s %(modify_window)s -e \
				'ssh -p %(port)d -o StrictHostKeyChecking=no -o ControlPath=~/.ssh/ssh_%(host)s_%(port)d.sock -o GSSAPIAuthentication=no %(timeout)s' %(source)s roo@%(host)s:%(dest)s" % \
				parameter
				send = subprocess.Popen(sendcmd,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True )
			else:
				sendcmd="rsync -avzc %s %s %s %s %s %s --bwlimit %s %s -e 'ssh -p %d -o StrictHostKeyChecking=no -o ControlPath=~/.ssh/ssh_%s_%d.sock -o GSSAPIAuthentication=no %s' %s root@%s:%s" \
					% (prune_empty_dirs_opt,include_opt,include_from_opt,exclude_opt,exclude_from_opt,delete_rsync,bwlimit,modify_window,\
				port,host,port,timeout,source,host,dest)
				send = subprocess.Popen(sendcmd,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True )
			#print sendcmd
			stdout,stderr = send.communicate()
			if send.returncode !=0:
				raise Exception(stderr)
		except Exception,err:
			message = '"fail","传送%s失败,失败信息%s"' % (source,err)
			print message
			raise Exception(message)
		finally:
			if drop_socket:
				try:
					delete_socket = subprocess.check_call(["ssh","-p",str(port),"-o","ControlPath=~/.ssh/ssh_%s_%d.sock"%(self.host,self.port),"-O","exit",self.host])
				except subprocess.CalledProcessError:
					message ='"warning","%s 没有后台ssh连接,不用退出"' % host
					print message
					syslog.syslog(syslog.LOG_WARNING,message)
		#获取传送速率
		bytes = re.search(r"(\d+\.?\d+) bytes/sec",stdout).group(1)
		KB = float(bytes)/1024
		return stdout,stderr,KB,send.returncode