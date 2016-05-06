#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__="lupuxiao"

import os
import sys
reload(sys)
import urllib2
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
import ConfigParser
import subprocess
from tools.colour import *
from tools.sendfile import Rsync_file
from client import down_xml
from tools.common import mkdir_p,ensure
'''
说明：同步选服列表脚本
由cdn_push_server_list.sh 改写
cdn 刷新 未写
'''

#在url中有http://xxx/server_list_xxx.xml url进行下载保存backup_path
def down_all_server_list(backup_path,url,verbose=True):
    res = None
    try:
        res = urllib2.urlopen(url)
        server_list = res.read()  
        if server_list == "":
            warn("%s中没有内容?请检查..."%url)
            exit(11)          
        for server in server_list.split():
            down_xml(backup_path,server,verbose)
    except urllib2.HTTPError,e:
        error('获取%s 状态码为: %s'%(url,e.code))
        exit(1)
    finally:
        if res:
            res.close()    


def parser_command():
    usage = '''%prog     
       -p    平台(qq,zh,vn,en,tw,i9) 
       -o    系统(andriod,ios,ios_yueyu)
       --ver    版本v1.1.5
       --test   测试模式
       eg:   %prog -p qq -o android --ver v1.1.5  同步qq选服列表知道cdn v1.1.5目录'''
    parser = OptionParser(usage=usage)
    parser.add_option("-o","--os",action="store",type="choice",choices=("ios","android","ios_yueyu"),dest="os",help="指定一种操作系统:ios,android,ios_yueyu",metavar="ios|android|ios_yueyu")
    parser.add_option("-p","--plat",action="store",type="str",dest="platform",help="指定平台:qq,zh,tw,en",metavar="qq|zh|tw|en")
    parser.add_option("--ver",action="store",type="str",dest="version",help="指定版本: v1.1.5",metavar="v1.1.5")
    parser.add_option("--clude",action="store",type="str",dest="clude",help="只包含渠道选服列表编号 --clude 000016,000019",metavar="000016,000019")
    parser.add_option("--exclude",action="store",type="str",dest="exclude",help="排除渠道选服列表编号 --exclude 010116,010119",metavar="010116,010119")
    parser.add_option("--test",action="store_true",dest="test",help="测试模式")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",help="显示更多信息")
    option,args = parser.parse_args()
    if not option.os or not option.platform or not option.version:
        parser.error("\033[1;31m3个选项必须同时指定..\033[0m")
    platforms =  cf.sections()
    if option.platform not in platforms:
        error("指定的(%s)语言不在配置文件中%s..请检查"%(option.platform,rsync_conf))
        exit(1)  
    if option.clude and option.exclude:
        error("指定的 --clude  和 --exclude 不能同时使用..")
        exit(1)           
    return (option,args)



def main(args):
    try:
        global cf,rsync_conf    
        cf = ConfigParser.ConfigParser()    
        ABSPATH=os.path.abspath(sys.argv[0])
        #conf 路径
        rsync_conf=os.path.dirname(ABSPATH)+"/rsync.conf"
        #列表路径
        server_list_path = os.path.dirname(os.path.dirname(ABSPATH)) + "/dzmo-client/server_list"
        mkdir_p(server_list_path)
        ##########################################  清空server_list目录 ##########################################
        os.popen("rm -rf %s/*"%server_list_path)
        cf.read(rsync_conf)
        #参数解析
        option,args = parser_command()
        #测试模式
        if option.test:
            Test = "true"
        else:
            Test = "false"
        if option.verbose:
            verbose = True
        else:
            verbose = False
        #排除选服xml
        exclude_str=None
        if option.exclude:  
            exclude_str="" 
            x=lambda tables: ["server_list_%s.xml"%t for t in tables.split(",")]
            exclude_str=x(option.exclude)

        #包含的xml
        clude_str=None
        if option.clude:
            clude_str=""
            for c in option.clude.split(","):
                c = "server_list_%s.xml"%c
                clude_str = clude_str + " " + c

        cdn_server = cf.get(option.platform,"server")
        cdn_user = cf.get(option.platform,"user")
        passfile = cf.get(option.platform,"passfile")  
        file_list = cf.get(option.platform,"file_list")
        cdn_dir = cf.get(option.platform,"dir")
        #目前H2没有other 这里暂时保留
        if option.platform == "tszn":
            file_list_url = "%s?os=%s&test=%s&other=%s"%(file_list,option.os,Test,option.platform)
        else:
            file_list_url = "%s?os=%s&test=%s&other="%(file_list,option.os,Test)
            #print file_list_url
        #下载server_list
        ##########################################  第一步 下载 server_list  ##########################################
        #print file_list_url
        down_all_server_list(server_list_path,file_list_url)
        #同步到cdn
        ##########################################  第二步 同步 server_list  ##########################################
        if clude_str:
            local_file_path = server_list_path + "/" + clude_str
        else:
            local_file_path = server_list_path + "/*"   
        sub_dir = option.os + "/server_list/" + option.version + "/"
        Rsync_file(passfile,cdn_user,cdn_dir,cdn_server,local_file_path,sub_dir,exclue_file=exclude_str,verbose=verbose)
        #cdn刷新
        if option.platform == "xmzh":
            for root,dirs,files in os.walk(server_list_path):
                for f in files:
                    url = "http://file.i2igame.com/devilprincess/android/server_list/%s/%s"%(option.version,f)
                    curl='''https://api.ccu.akamai.com/ccu/v2/queues/default -H "Content-Type:application/json" -d '{"objects" : ["%s"]}' -u haoyue612@163.com:"haoyue612"'''%url
                    cmd = "curl %s"%curl
                    #print cmd
                    run = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                    stdout,stderr = run.communicate()
                    if run.returncode != 0:
                        print stderr,stdout
                    else:
                        if eval(stdout)["httpStatus"] == 201:
                            success("/%s/%s 刷新成功..."%(option.version,f))

        #pass
    except IOError,err:
        warn(err)
    except KeyboardInterrupt:
        warn("程序被强行停止!!") 
    except Exception,err:
        raise Exception(err) 

if __name__ == "__main__":
    main(sys.argv)

