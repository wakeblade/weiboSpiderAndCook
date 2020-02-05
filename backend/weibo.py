# !/usr/bin/env python
# -*- coding: UTF-8 -*-

import collections
import requests
import time
from datetime import datetime,timedelta
import csv
import os
import random

from fastspider import Spider

#用户保存数据
User = collections.namedtuple('User','id screen_name profile_image_url profile_url gender followers_count follow_count verified_type')
#微博保存数据
#Weibo = collections.namedtuple('Weibo','itemid scheme created_at id text textLength userid reposts_count comments_count attitudes_count obj_ext')
Weibo = collections.namedtuple('Weibo','itemid scheme created_at id text userid reposts_count comments_count attitudes_count')

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

Config={
    'ENTRY_USERID': '3325704142',   #入口用户ID
    'MIN_FANS': 10000,               #样本最少粉丝数
    'MAX_FANS': 50000000,           #样本最多粉丝数
    'MIN_IDS':5000,                 #样本最少ID数
    'MAX_IDS':10000,                 #样本最多ID数
    'MAX_DAYS':7,                   #爬取内容离今天最远天数
    'BUFFER_SIZE':200,              #微博解析缓存
    #'DB_NEED':1,                   #是否使用数据库
    'DB_TYPE':'mongo',              # 支持mongo & mysql & redis，如果为空则不使用数据库保存数据  
    'DB_CFG':{                      #数据库的连接配置
        'url':'',
        'host':'',
        'port':17201,
        'user':'admin',
        'pwd':'abc123'
    },
    'URL_FOLLOWS_FIRST':'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}',
    'URL_FOLLOWS_PAGE':'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}&page={}',
    'URL_WEIBO_FIRST':'https://m.weibo.cn/api/container/getIndex?containerid=107603{}',
    'URL_WEIBO_PAGE':'https://m.weibo.cn/api/container/getIndex?containerid=107603{}&page={}',
}
"""
'ERROR_DELAY':10,               #反爬延迟
'PAGE_DELAY':1,                 #单页延迟
'RANDOM_SEED':3,                #单页延迟
"""

#缓存表
#用户表
ids_queue=[Config['ENTRY_USERID']]
ids_history=[]
tb_users={}
users_buffer ={} 
#粉丝关系表
tb_follows={}
#微博内容表
tb_weibos={}
weibos_buffer ={} 

#计时器
startTime = time.perf_counter()

"""
从txt读取数据，转换成list
"""
def txt2list(filename):
    l =[]
    with open(filename) as f:
        l=list(f)
    return l

valid_ips = txt2list("./valid_ips.txt")

"""
保存字典数据为csv
"""
def dict2csv(filename,m,d):
    with open(filename,m,encoding='UTF-8',newline='') as f:
        fw =csv.writer(f)
        fw.writerows(d)
        f.close()

"""
保存爬取的数据为csv
"""
def ntdict2csv(filename,d,NT):
    size = os.path.getsize(filename) if os.path.exists(filename) else 0
    with open(filename,'a',encoding='UTF-8',newline='') as f:
        fw =csv.writer(f)
        if size ==0 :
            fw.writerow(NT._fields)
        for i in d.values():
            fw.writerow(i)
        f.close()

"""
从csv读取数据，转换成NamedTuple字典
"""
def csv2ntdict(filename,NT):
    if not os.path.exists(filename):
        return {}

    d={}
    with open(filename,'r',encoding='UTF-8') as f:
        fr =csv.reader(f)
        next(fr)
        for i in fr:
            #print(i)
            if(len(i)>0):
                nt = NT(*i)
                d[nt.id]=nt
        f.close()
    return d

"""
解析用户信息
'id screen_name profile_image_url profile_url gender followers_count follow_count verified_type'
"""
def parseUser(js):
    #print('t=========',js)
    #print('t.keys()=========',js.keys())
    user =User(
        js['user']['id'],
        js['user']['screen_name'],
        js['user']['profile_image_url'],
        js['user']['profile_url'],
        js['user']['gender'],
        js['user']['followers_count'],
        js['user']['follow_count'],
        js['user']['verified_type'],
    )
    return user

"""
判断用户是否新的
"""
def isUserNeedToAdd(user):
    if(int(user.verified_type)!=0):
        return False
    if(user.followers_count<int(Config['MIN_FANS']) or user.followers_count>int(Config['MAX_FANS'])):
        return False
    if(user.id in tb_users):
        return False
    return True

"""
添加粉丝关系
"""
def addFollow(userid,followid):
    l = tb_follows.setdefault(userid,[])
    if followid not in l:
        l.append(followid)

"""
获取某个用户ID的Follows
"""
def spiderId(userId):
    spider =Spider(header=header)
    global users_buffer
    #print("userId==========",userId)
    #获取关注者列表
    url = Config['URL_FOLLOWS_FIRST'].format(userId)
    #print("url==========",url)

    """抓取关注列表第一页,计算分页数和全部关注的位置"""
    # js = requests.get(url,headers=header).json()
    js = spider.url(url).json()
    #print("==========js==========",js)
    total_follows = js['data']['cardlistInfo']['total']
    #print("==========follow_total==========",follow_total)
    page_follows = len(js['data']['cards'][-1]['card_group'])
    #print("==========page_follows_number==========",page_follows_number)
    total_pages = total_follows // page_follows
    #该api默认最多抓取10页
    total_pages = min(10,total_pages)
    #print("==========pages_number==========",pages_number)
    #获取全部关注cards位置
    #all_follows_index = len(js['data']['cards'])

    p=1
    while p<=total_pages:
        url = Config['URL_FOLLOWS_PAGE'].format(userId,str(p))
        print('页面：{}/{}==========='.format(str(p),str(total_pages)))
        js = spider.url(url).json()                
        #print("len(js['data']['cards'])====",len(js['data']['cards']))
        count=0
        if js['data']['cards']:
            for f in js['data']['cards'][-1]['card_group']:
                #print('f================',f)
                #print(f['user']['id'],'  :  ',f['user']['screen_name'],'  被粉数:  ',f['user']['followers_count'], '  粉人数:  ', f['user']['follow_count'])
                user =parseUser(f)
                if(isUserNeedToAdd(user)):
                    users_buffer[user.id]=user
                    print('user{}/{}({}s)==========={}-{}'.format(str(len(ids_queue)),str(len(tb_users)),int(time.perf_counter()-startTime),user.screen_name,user.verified_type))
                    #保存粉丝关系
                    addFollow(userId,user.id)
                    #print('ids_queue===========',ids_queue)
                    #print('ids_history===========',ids_history)
                    if (user.id not in ids_queue) and (user.id not in ids_history):
                        ids_queue.append(user.id)
                        #print('user{}==========='.format(str(len(tb_users))),user)
                    count+=1
                    #spiderIds(user.id)
        if(len(users_buffer)>Config['BUFFER_SIZE']):
            ntdict2csv("./tb_users.csv",users_buffer,User)
            tb_users.update(users_buffer)
            users_buffer={}
            print('已爬取用户{}============='.format(len(tb_users)))
        p+=1
    if(userId not in ids_history):
        ids_history.append(userId)

"""
获取符合条件的所有微博ID样本
"""
def spiderIds():
    while (len(ids_queue)>0 and len(tb_users)<int(Config['MAX_IDS'])):
        userId = ids_queue.pop()
        spiderId(userId)
    ntdict2csv("./tb_users.csv",tb_users,User)
    dict2csv("./tb_follows.csv",'w+',tb_follows)

"""
解析微博信息
'itemid scheme created_at id text textLength userid reposts_count comments_count attitudes_count obj_ext'
"""
def parseWeibo(js):
    #print('t=========',js)
    #print('t.keys()=========',js.keys())
    weibo =Weibo(
        js['itemid'],
        js['scheme'],
        repaireDate(js['mblog']['created_at']),
        js['mblog']['id'],
        js['mblog']['text'],
        #js['mblog']['textLength'],
        js['mblog']['user']['id'],
        js['mblog']['reposts_count'],
        js['mblog']['comments_count'],
        js['mblog']['attitudes_count'],
        #js['mblog']['obj_ext'],
    )
    return weibo

"""
日期修复
"""
def repaireDate(created_at):
    """标准化微博发布时间"""
    if u"刚" in created_at:
        created_at = datetime.now().strftime("%Y-%m-%d")
    elif u"分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
    elif u"小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
    elif u"昨天" in created_at:
        day = timedelta(days=1)
        created_at = (datetime.now() - day).strftime("%Y-%m-%d")
    elif created_at.count('-') == 1:
        year = datetime.now().strftime("%Y")
        created_at = year + "-" + created_at
    return created_at

"""
判断用户是否新的
"""
def isWeiboNeedToAdd(weibo):
    if(weibo.id in tb_weibos or weibo.id in weibos_buffer):
        return False
    if((datetime.now()- datetime.strptime(weibo.created_at,'%Y-%m-%d')).days<int(Config['MAX_DAYS'])):
        return False
    return True

"""
获取某个用户ID的Follows
"""
def spiderWeibo(userId):
    spider =Spider(header=header)
    global weibos_buffer
    #print("userId==========",userId)
    #获取关注者列表
    url = Config['URL_WEIBO_FIRST'].format(userId)
    #print("url==========",url)

    """抓取关注列表第一页,计算分页数和全部关注的位置"""
    js = spider.url(url).json()
    #print("==========js==========",js)
    total_weibos = js['data']['cardlistInfo']['total']
    #print("==========total_weibos==========",total_weibos)
    page_weibos = len(js['data']['cards'])
    #print("==========page_follows_number==========",page_follows_number)
    total_pages = total_weibos // page_weibos

    p=1
    count=0
    while p<=total_pages:
        url = Config['URL_WEIBO_PAGE'].format(userId,str(p))
        print('页面：{}/{}==========='.format(str(p),str(total_pages)))
        js = spider.url(url).json()                
        #print("len(js['data']['cards'])====",len(js['data']['cards']))
        #print(js['data']['cards'])
        for f in js['data']['cards']:
            #print('f================',f)
            if(f['card_type']!=9):
                continue
            weibo =parseWeibo(f)
            if(isWeiboNeedToAdd(weibo)):
                weibos_buffer[weibo.id]=weibo
                #print('weibo {}/{}==========='.format(str(count),str(total_weibos)),weibo)
                print('weibo {}/{}({}s)==========='.format(str(count),str(total_weibos),int(time.perf_counter()-startTime)))
            count+=1
        if(len(weibos_buffer)>Config['BUFFER_SIZE']):
            ntdict2csv("./tb_weibos.csv",weibos_buffer,Weibo)
            tb_weibos.update(weibos_buffer)
            weibos_buffer={}
            print('已爬取微博{}============='.format(len(tb_weibos)))
        p+=1

"""
获取符合条件的所有微博ID样本
"""
def spiderWeibos():
    userids = [user.id for user in tb_users.values()]
    random.shuffle(userids)
    count=0
    for id in userids:
        spiderWeibo(id)
        count+=1
        print('已爬取人数{}/{}============='.format(count,len(userids)))
    ntdict2csv("./tb_weibos.csv",tb_weibos,Weibo)

##############################################################
def get_json(url, params):
    """获取网页中json数据"""
    r = requests.get(url, params=params)
    return r.json()

def get_id_json(userId, page):
    """获取网页中微博json数据"""
    params = {'containerid': '107603' + userId, 'page': page}
    js = get_json(params)
    return js

"""
获取某个ID的所有微博
"""
def spiderPosts(userId):
    pass

"""
载入已保存的用户ID样本
"""
def loadIds(config):
    pass


"""
将用户id拼接成个人主页的URL
"""
def getProfileUrl(userId):
    pass

"""
将用户id拼接成微博主页的URL
"""
def getWeiboUrl(userId):
    pass

"""
将微博id拼接成微博详情页的URL
"""
def getPostUrl(postId):
    pass

if __name__=='__main__':
    #入口用户ID
    tb_users = csv2ntdict("./tb_users.csv",User)
    #print(tb_users)
    #spiderIds()

    tb_weibos = csv2ntdict("./tb_weibos.csv",Weibo)
    #print(tb_weibos)
    spiderWeibos()