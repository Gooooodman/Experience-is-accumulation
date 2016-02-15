#!/usr/bin/python
# -*- coding: utf-8 -*-
#author yyr lupuxiao
'''自定义的线程模块'''
import threading

class threads(threading.Thread):
	'''创建线程类threading.Thread的子类

	把功能函数作为参数传递去执行不同的功能,同时把其余的参数都传递到功能函数当中'''
        def __init__(self,function,*parameter):
		threading.Thread.__init__(self)
		self.function = function
		self.parameter = parameter
	def run(self):
		self.function(*self.parameter)

def ThreadQueue (function,parallel,inqueue,*parameter):
	'''定义多线程函数与队列结合控制多线程运行

	队列(queue)要作为function的参数function(queue)'''

	for i in range(parallel):	
		t = threads(function,inqueue,*parameter)
		t.setDaemon(True)
		t.start()
	#等所有队列的任务完成
	inqueue.join()

