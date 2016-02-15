#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__="lupuxiao" 

'''
设置颜色
对字符串进行包装
'''

def setcolour(colour="important"):
    if colour == "red":        
        def _colour(f):
            def _wrapped(*arg):
                print '\033[1;31m"fail",%s\033[0m'%f(arg)
            return _wrapped
        return _colour
    elif colour == "yellow":
        def _colour(f):
            def _wrapped(*arg):
                print '\033[1;33m"warning",%s\033[0m'%f(arg)
            return _wrapped
        return _colour               
    elif colour == "blue":
        def _colour(f):
            def _wrapped(*arg):
                print '\033[1;32m"success",%s\033[0m'%f(arg)
            return _wrapped
        return _colour         
    else:
        def _colour(f):
            def _wrapped(*arg):
                print '\033[33;41m"important"\033[0m,%s'%f(arg)
            return _wrapped
        return _colour   



#颜色调用示例
@setcolour("red")
def error(arg):
    return arg

@setcolour("blue")
def success(arg):
    return arg

@setcolour("yellow")
def warn(arg):
    return arg

@setcolour()
def important(arg):
    return arg
