#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,re,sys
from common import confirm,Progress,OtherException
from colour import warn,success,error
import subprocess
import time
__author__="lupuxiao"

'''
作用：传输文件
参数说明
passfile              rsync 密码文件
rsync_user            rsync 用户
rsync_dir             rsync的 根目录如dizun,dzmo
cdn_server            cdn服务器
local_file_path      本地文件路径
rsync_sub_dir        cdn上的目录如：android 则最后会命令为 ::dzmo/android
count                 大文件不断输出传输过程 ---传资源使用
'''

def Rsync_file(passfile,rsync_user,rsync_dir,cdn_server,local_file_path,rsync_sub_dir,exclue_file=None,rsync_opts='-Ratpv',sshconnect=None,verbose=False,count=False):
    #local_dir 进入目录
    local_dir=os.path.split(local_file_path)[0]
    #传送的文件
    send_file=os.path.split(local_file_path)[1]
    exclude_opt = ""
    ########################错误收集########################
    nofile=re.compile("failed: No such file or directory") 
    permission = re.compile("by root when running as root") 
    ########################错误收集########################
    if exclue_file != None:
        if type(exclue_file) is list:
            for f in exclue_file:
                exclude_opt += "--exclude %s  " % f
        else:
            warn("排除文件必须是一个list")
            exit(1)
    
    #远程调用  
    try:
        if sshconnect:
            cmd = '''"cd %s && rsync --password-file=%s %s %s %s %s@%s::%s/%s"'''%(local_dir,passfile,rsync_opts,send_file,exclude_opt,rsync_user,cdn_server,rsync_dir,rsync_sub_dir)
            print '\033[1;33mcmd: %s\033[0m'%cmd
            confirm()
            print "\033[1;32m正在远程执行操作....\033[0m"
            print "正在同步中.请等待....."
            stdout,stderr,returncode = sshconnect.run(cmd,drop_socket=False)  
        else:
            cmd = "cd %s && rsync --password-file=%s %s %s %s %s@%s::%s/%s"%(local_dir,passfile,rsync_opts,send_file,exclude_opt,rsync_user,cdn_server,rsync_dir,rsync_sub_dir)
            print '\033[1;33mcmd: %s\033[0m'%cmd
            confirm()
            print "正在同步中.请等待....."
            run = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            if count:
                while run.poll() == None:
                    line = run.stdout.readline()
                    print line.strip("\n")
            else:
                while run.poll() == None:
                    Progress()
                stdout,stderr = run.communicate()        
            returncode = run.returncode

        if returncode != 0:
            message=stderr.strip("\n")        
            if nofile.findall(message):
                warn("没有文件可传!!! 3s后继续...")
                time.sleep(3)
            elif permission.findall(message):
                warn("使用的用户不对,请检查...")
                exit(1)
            else:
                #抛出异常   
                raise OtherException(message)             
        else:                
            if verbose:
                if count == False:
                    print("\033[1;32m#########################信息如下#########################\033[0m")
                    print stdout.strip("\n") 
                    print("\033[1;32m##########################################################\033[0m")
            success("rsync 传送成功...")
    except OtherException,err:
        error(err)
    except Exception,err:
        message = '\033[1;31m"fail",rsync 失败,信息:%s,%s,%s\033[0m'%(err,stdout,stderr)
        error(message)
