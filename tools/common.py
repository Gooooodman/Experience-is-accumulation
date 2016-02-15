#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
from colour import error
__author__="lupuxiao" 



#保存一些公共的函数
#

'''
格式：qq_s1,qq_s3~qq_s8,iso_s11,iso_yueyu_s3
结果：['qq_s1', 'qq_s3', 'qq_s4', 'qq_s5', 'qq_s6', 'qq_s7', 'qq_s8', 'iso_s11', 'iso_yueyu_s3']
'''

def split_single(singles):
    '''
    对qq_s1,qq_s3~qq_s8,iso_s11,iso_yueyu_s3进行分离得出单服列表
    '''
    all_servers=[]
    for server_list in singles.split(","):
        r=re.compile("~")
        if r.findall(server_list):
            plat1=server_list.split("~")[0]
            m=re.search(r'(^[A-Z,a-z,0-9]+_(s|x))([0-9]+$)',plat1)
            if m:
                h_plat1=m.group(1)
                plat1_id=int(m.group(3))
            else:
                print " %s 格式有误 "%plat1
                exit()
 
            plat2=server_list.split("~")[1]
            m=re.search(r'(^[A-Z,a-z,0-9]+_(s|x))([0-9]+$)',plat2)
            if m:
                h_plat2=m.group(1)
                plat2_id=int(m.group(3))
            else:
                print " error 格式有误 %s "%plat2
                exit()
 
            if h_plat1 == h_plat2:
                pass
            else:
                print "平台不相同 %s and %s "%(plat1,plat2)
                exit()
 
            if plat1_id < plat2_id:
                pass
            else:
                print "格式有误 %s and %s "%(plat1,plat2)
                exit()
            for id in range(int(plat1_id),int(plat2_id)+1):
                agent=h_plat1+str(id)
                all_servers.append(agent)
        else:
            all_servers.append(server_list)
    return  all_servers

#确认
def confirm():
    while True:
        anwser = raw_input("确认cmd无误请按yes,取消输入no\t")
        if re.match(r"yes",anwser,re.I):
            break
        elif re.match(r"no",anwser,re.I):
            exit(1)

#判断文件与目录
def ensure(path):
    if not os.path.isfile(path) and not os.path.isdir(path):
        error("%s,不存在!!请检查.."%path)
        exit(1)





# 等同于mkdir -p 
def mkdir_p(path):
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
    except OSError as exc:
        raise




def Progress(info="Progressing:",sleep=0.3):
    ls=["-","\\","|","/"]
    for i in  ls:
        time.sleep(sleep)
        sys.stdout.write("%s %s   \r" %(info,i))
        sys.stdout.flush()    

class OtherException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)




