#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__="lupuxiao"

import os
import sys
reload(sys)
import urllib2
import datetime
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
import ConfigParser
from tools.common import mkdir_p
from tools.colour import *
from tools.sendfile import Rsync_file
from tools.ssh import ssh
'''
说明：正式模式更新脚本
由client_xxx.sh 改写
'''


#流程
#
#因为在测试模式已经把update_000xxx.xml放在了测试服的/data/web/dzmo/client/android目录
#1.备份一份
#2.只需要把相关update 传到cdn 
#3.cdn刷新 未完成


#建议从测试服同步到cdn的rsync密码文件与163的位置进行统一管理,就不用写多分配置文件
#建议统一格式: /data/yunwei/rsync_pass/rsync_平台.pass  下存放,如rsync_tl.pass  rsync_i9.pass




#这里填2个参数,可以重复使用
def down_xml(backup_path,url,verbose=False):
    channel_xml = url.split("/")[-1]
    res = None
    try:
        res = urllib2.urlopen(url)
        if verbose:
            success("%s 备份/下载成功..."%channel_xml)
        file = open("%s/%s"%(backup_path,channel_xml),"w")
        file.write(res.read())
        file.close()
    except urllib2.HTTPError,e:
        error('获取%s 状态码为: %s'%(url,e.code))
    finally:
        if res:
            res.close()    



def parser_command():
    usage = '''%prog
       提示：首次系统(如:ios_yueyu)在cdn上是没有update_xxx.xml文件的,需手动上传一个xml上去在修改rsync.conf 备份的渠道号,在执行。     
       -p, --plat     平台(qq,zh,vn,en,tw,i9) 
       -o, --os       系统(andriod,ios,ios_yueyu)
       -s,--single    单个update_000xx.xml
       -v,--verbose   显示更多信息
       eg:   %prog -p qq -o android 更新qq安卓到正式模式  | -s update_0002.xml  只传输单个文件'''
    parser = OptionParser(usage=usage)
    parser.add_option("-o","--os",action="store",type="choice",choices=("ios","android","ios_yueyu"),dest="os",help="指定一种操作系统:ios,android,ios_yueyu",metavar="ios|android|ios_yueyu")
    parser.add_option("-p","--plat",action="store",type="str",dest="platform",help="指定平台:qq,zh,tw,en",metavar="qq|zh|tw|en")
    parser.add_option("-s","--single",action="store",type="str",dest="single_file",help="指定单个update__xxx.xml:update_0002.xml",metavar="update__xxx.xml")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",help="显示更多信息")
    option,args = parser.parse_args()
    if not option.os or not option.platform:
        parser.error("\033[1;31m2个选项必须同时指定..\033[0m")
    platforms =  cf.sections()
    if option.platform not in platforms:
        parser.error("\033[1;31m指定的(%s)语言不在配置文件中%s..请检查\033[0m"%(option.platform,rsync_conf)) 
    return (option,args)




def main(args):
    global cf,rsync_conf    
    cf = ConfigParser.ConfigParser()    
    ABSPATH=os.path.abspath(sys.argv[0])
    #conf 路径
    rsync_conf=os.path.dirname(ABSPATH)+"/rsync.conf"
    cf.read(rsync_conf)
    ############变量区域###########    
    #当前时间格式2016-01-06_13-36
    nowtime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    #参数解析
    option,args = parser_command()    
    #备份路径
    backup_path = "/data/backup/%s/%s/%s"%(option.platform,option.os,nowtime)
    #创建备份目录
    mkdir_p(backup_path)

    test_port = cf.getint("test","port")
    test_ip  = cf.get("test","server")
    #update存放在测试服上的位置
    client_dir = cf.get("test","client_dir") 
    #rsync信息
    cdn_server =  cf.get(option.platform,"server")
    cdn_user = cf.get(option.platform,"user")
    #test_passfile 是代表测试服务器存在pass的路径,后续与163进行统一存放
    cdn_pass_file = cf.get(option.platform,"passfile")
    cdn_dir = cf.get(option.platform,"dir")
    cdn_url = cf.get(option.platform,"url")
    lang = cf.get(option.platform,"lang")
    #需要备份的update url
    back_update = cf.get(option.platform,"back_channel_%s"%option.os)
    if not back_update:back_update="update_%s_%s.xml"%(lang,option.os)
    back_update_url = cdn_url + "/" + option.os +"/" + back_update
    #备份
    down_xml(backup_path,back_update_url,verbose=option.verbose)
    #连接测试服
    try:
        SSH = ssh(host=test_ip,port=test_port)
        if option.platform == "qq":
            update_xml = "update_000028.xml update_000184.xml"
            local_file_path = client_dir + update_xml
            #存放cdn 目录
            Rsync_file(cdn_pass_file,cdn_user,cdn_dir,cdn_server,local_file_path,option.os,sshconnect=SSH,verbose=option.verbose)
        elif option.single_file: 
            local_file_path = client_dir + option.single_file
            Rsync_file(cdn_pass_file,cdn_user,cdn_dir,cdn_server,local_file_path,option.os,sshconnect=SSH,verbose=option.verbose)
        else:
            #排除一些文件
            local_file_path = client_dir + "*"
            #如果要排除一些文件,使用下面的格式,exclue_file=excule_xml
            excule_xml =[ e for e in cf.get(option.platform,"exclude_update").split(",")]
            if len(excule_xml) == 0 or excule_xml[0] == "":
                excule_xml=None
            Rsync_file(cdn_pass_file,cdn_user,cdn_dir,cdn_server,local_file_path,option.os,sshconnect=SSH,exclue_file=excule_xml,verbose=option.verbose)
 
    except KeyboardInterrupt:
        warn("程序被强行停止!!") 
    except Exception,err:
        error(err) 


#刷新未写




if __name__ == "__main__":
    main(sys.argv)



