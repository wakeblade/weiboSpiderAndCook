# !/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
from gevent import monkey
monkey.patch_all()
from gevent.queue import Queue
"""
import requests
import time
import random

proxies=[]
with open('./ips.txt') as f:
    proxies = [line.split('@')[0] for line in f]
def randomProxy(proxies):
    ip = random.choice(proxies)
    return {'https':ip,'http':ip}

class Task:
    def __init__(self,url=None,method='get',params=None,data=None,cookie=None):
        self.url=url
        self.method=method
        self.params=params
        self.data=data
        self.cookie=cookie

    def __str__(self):
        return str(self.__dict__)

class Spider:
    methods ={
        'get':requests.get,
        'post':requests.post,
        'put':requests.put,
        'delete':requests.delete,
        'head':requests.head
    }
    config ={
        'ERROR_DELAY':10,               #反爬延迟
        'PAGE_DELAY':1,                 #单页延迟
        'RANDOM_SEED':3,                #单页延迟
    }

    def __init__(self,header=None,proxy=None,timeout=None,config=None):
        self.header=header
        self.proxy=proxy
        self.timeout=timeout
        if config:
            self.update(config)

    def __str__(self):
        return str(self.__dict__)

    def url(self,url):
        task =Task(url)
        return self.task(task)

    def task(self,task):
        if task.url==None:
            raise('Error:爬虫任务url不能为空!')
        self.method ='get' if task.method==None else task.method
        kwargs={'url':task.url}
        if self.header:
            kwargs['headers']=self.header
        if self.proxy:
            kwargs['proxies']=self.proxy
        if self.timeout:
            kwargs['timeout']=self.timeout
        if task.params:
            kwargs['params']=task.params
        if task.cookie:
            kwargs['cookies']=task.cookie
        if task.data:
            kwargs['data']=task.data
        #print("\n{} \n- {}\n".format(self,task))
        delay=random.randint(0,self.config['RANDOM_SEED'])
        while True:
            try:
                res = self.methods[self.method](**kwargs)
            except Exception as e:
                #print(e)
                kwargs['proxies']=randomProxy(proxies)
                print('(延迟{}s)==={}==={}'.format(str(delay),kwargs['proxies'],task.url))
                delay+=1
                time.sleep(delay*self.config['ERROR_DELAY'])
            else:
                time.sleep(delay*self.config['PAGE_DELAY'])
                break

        return res

"""
url = 'http://icanhazip.com'
header ={
    'Accept':'*/*',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Language':'zh-CN',
    'Accept-Encoding':'gzip, deflate',
    #'Connection': 'Keep-Alive',
    'Connection': 'close',
    'Cache-Control': 'no-cache',
    'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.01)'
}

task1=Task(url=url,method='post')
task2=Task(url)
#spider =  Spider(header,randomProxy(proxies),(2,2))
spider =  Spider()
#print(spider.task(task2).text)
print(spider.url(url).text)
#t = timeit.timeit(stmt='spider(task1.proxies(randomProxy(proxies)))',setup='from __main__ import spider,task1,randomProxy,proxies',number=10)
#print(t)
"""