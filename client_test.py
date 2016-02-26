#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__="lupuxiao"

import os
import sys
reload(sys)
import re
import urllib2
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
import ConfigParser
import subprocess 
from tools.common import ensure,OtherException
from tools.colour import *
from tools.sendfile import Rsync_file
import xml.etree.ElementTree as ET 

'''
说明：测试模式更新脚本
由client_xxx_test.sh 改写

'''


#返回dir
def get_update_dir(url):
    #print url
    res = None
    try:
        res = urllib2.urlopen(url)
        lines = res.read()
        root = ET.fromstring(lines)
        nodes=root.getiterator("root")
        for n in nodes :
            return n.attrib.get("dir")
    except urllib2.HTTPError,e:
        error('获取%s 状态码为: %s'%(url,e.code))
    finally:
        if res:
            res.close()


#切换cdn资源目录 a->b ,b->a
def change_cdn_res_dir(url_update_xml):
    #对update_lang_os.xml 进行交换dir属性
    url_dir = get_update_dir(url_update_xml)
    #print "cdn资源目录为: ",url_dir
    if url_dir == "a":
        change_cdn_dir = "b"
    else:
        change_cdn_dir = "a"

    cmd = r'''sed -i -r 's/(dir=)"[^"]*"/\1"%s"/' %s'''%(change_cdn_dir,update_xml_file)
    ret = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = ret.communicate()
    if ret.returncode != 0:
        message="切换cdn %s 资源目录失败:%s,%s"%(url_update_xml,stdout.strip("\n"),stderr.strip("\n"))
        print message
        exit(1) 
    return change_cdn_dir



def parser_command():
    usage = '''%prog     
       -p    平台(qq,zh,vn,en,tw,i9) 
       -o    系统(andriod,ios,ios_yueyu)
       eg:   %prog -p qq -o android 国服安卓'''
    parser = OptionParser(usage=usage)
    parser.add_option("-o","--os",action="store",type="choice",choices=("ios","android","ios_yueyu"),dest="os",help="指定一种操作系统:ios,android,ios_yueyu",metavar="ios|android|ios_yueyu")
    parser.add_option("-p","--plat",action="store",type="str",dest="platform",help="指定平台:qq,zh,tw,en",metavar="qq|zh|tw|en")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",help="显示更多信息")
    option,args = parser.parse_args()
    if not option.os or not option.platform:
        parser.error("\033[1;31m2个选项必须同时指定..\033[0m")
    platforms =  cf.sections()
    if option.platform not in platforms:
        error("指定的(%s)语言不在配置文件中%s..请检查"%(option.platform,rsync_conf))
        exit(1) 

    return (option,args)


def main(argv):  

    ##############变量区域##################

    global  rsync_conf,cf,update_xml_file
    #脚本绝对路径
    ABSPATH=os.path.abspath(sys.argv[0])
    #临时存在文件目录
    #update.xml 这里目前获取的是admin下的update_xxx_xxx.xml 后续生成h2 在更换
    #work_dir = "/home/yansheng/admin/dzmo-client/"    
    work_dir = os.path.dirname(os.path.dirname(ABSPATH)) + "/dzmo-client/"
    #配置文件路径
    rsync_conf=os.path.dirname(ABSPATH)+"/rsync.conf"
    is_qq = "false"
    ##############变量区域##################
    cf = ConfigParser.ConfigParser() 
    cf.read(rsync_conf)    
    option,args = parser_command()

    try:
        #更新测试环境,update.xml
        test_cdn_server = cf.get("test","server")
        test_user = cf.get("test","user")
        test_passfile = cf.get("test","passfile")
        test_rsync_dir = cf.get("test","dir")
        test_lang = cf.get("test","lang")
        #获取平台 cdn server 一些变量
        cdn_server = cf.get(option.platform,"server")
        user = cf.get(option.platform,"user")
        passfile = cf.get(option.platform,"passfile")
        rsync_dir = cf.get(option.platform,"dir")
        url = cf.get(option.platform,"url")
        ##lang lang2 在api 与 update_zh_xx.xml 不同 以便区分,后续统一进行更改
        lang = cf.get(option.platform,"lang")
        lang2 =  cf.get(option.platform,"lang2")       
        #update.xml  都保存在测试服的::dzmo/android
        test_update_xml_dir = cf.get("test","update_xml_dir")
        #先通过./gen_update_xml.escript android zh 获取update
        #################第一步: 更新update_xml到测试服182##############
        lang_work_dir = "%s%s/%s/"%(work_dir,lang,option.os)
        update_xml = "update_%s_%s.xml"%(lang,option.os)
        update_xml_file = lang_work_dir + update_xml
        #判断update_xx_xx.xml是否存在
        ensure(update_xml_file)
        #开始同步到测试服
        Rsync_file(test_passfile,test_user,test_rsync_dir,test_cdn_server,update_xml_file,test_update_xml_dir,verbose=option.verbose)

        #################第二步：同步资源到测试服##############
        res_dir=lang_work_dir + "latest/"
        #判断资源目录是否存在
        ensure(res_dir)
        #资源文件为* (全部)
        res_file = res_dir + "*"

        #update_xx_xx.xml  url
        if option.platform == "qq":
            url = cf.get(option.platform,"url")
            url_update_xml = url + option.os + "/"+ "update_000028.xml"
            cdn_dir = get_update_dir(url_update_xml)
            if cdn_dir == "c":
                change_cdn_dir = "d"
            else:
                change_cdn_dir = "c" 
            is_qq = "true"               
        else:
            #url_update_xml 源站 update_zh_android.xml第一次要传上去
            #android
            #http://mwygzres.game13.com/android/
            url_update_xml = url + option.os + "/" + update_xml
            #对资源目录进行切换
            change_cdn_dir = change_cdn_res_dir(url_update_xml)
            #print change_cdn_dir
        rsync_path = option.os+"/"+change_cdn_dir
        #开始同步资源到cdn
        Rsync_file(passfile,user,rsync_dir,cdn_server,res_file,rsync_path,verbose=option.verbose)


        #################第三步：CDN刷新##############
        #目前国内,英语有提供,其它未提供
        #后续补充


        #################第四步：生成各渠道update_xxx.xml到测试模式##############

        #update_xml 目录            
        update_xml_dir = work_dir + "update_xml/"
        if os.path.isdir(update_xml_dir):
            #如果存在
            os.popen("rm -f  %s/*"%update_xml_dir)
        else:
             os.mkdir(update_xml_dir) 

        api_url= cf.get(option.platform,"api_url")
        #h2  update API 
        api = "%s?os=%s&need_update=true"%(api_url,option.os)
        #检查接口返回值是否正确
        try:
            res = None
            res = urllib2.urlopen(api)
            lines = res.read().strip("\n")
            ok = re.compile("ok:")
            if not ok.findall(lines):
                message="执行%s没有获取到OK信息为: %s"%(api,lines)
                raise OtherException(message)
        except urllib2.HTTPError,e:
            message = '获取%s 状态码为: %s'%(api,e.code)
            error(message)
        except OtherException,err:
            error(err)          
        finally:
            if res:
                res.close()        

        xmls=lines.split("\n")
        for xml in xmls:
            if not ok.findall(xml):
                #下载xml
                xml_file = xml.split("/")[-1]
                #print xml_file
                res = urllib2.urlopen(xml)
                file = open("%s/%s"%(update_xml_dir,xml_file),"w")
                file.write(res.read())
                file.close()
                if option.verbose:
                    print xml_file," 已下载成功.."

        ##同步update_000xx.xml到测试服
        update_xml_file = update_xml_dir+"*"
        Rsync_file(test_passfile,test_user,test_rsync_dir,test_cdn_server,update_xml_file,test_update_xml_dir,verbose=option.verbose)

    except IOError,err:
        warn(err)
    except NameError,err:
        warn(err) 
    #捕获键盘中断         
    except KeyboardInterrupt:
        warn("程序被强行停止!!")   
    except Exception,err:
        error(err)


if __name__ == "__main__":
    main(sys.argv)









