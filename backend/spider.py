# !/usr/bin/env python
# -*- coding: UTF-8 -*-

import collections
import requests
import time
from datetime import datetime,timedelta
import csv

#用户保存数据
User = collections.namedtuple('User','id screen_name profile_image_url profile_url gender followers_count follow_count')
#微博保存数据
#Weibo = collections.namedtuple('Weibo','itemid scheme created_at id text textLength userid reposts_count comments_count attitudes_count obj_ext')
Weibo = collections.namedtuple('Weibo','itemid scheme created_at id text userid reposts_count comments_count attitudes_count')

proxies = {
  "http": "http://10.10.1.10:3128",
  "https": "http://10.10.1.10:1080",
}

header ={
    'Accept':'*/*',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Language':'zh-CN',
    'Accept-Encoding':'gzip, deflate',
    'Connection': 'Keep-Alive',
    'Cache-Control': 'no-cache',
    'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.01)'
}

Config={
    'ENTRY_USERID': '1195242865',   #入口用户ID
    'MIN_FANS': 5000,               #样本最少粉丝数
    'MAX_FANS': 50000000,           #样本最多粉丝数
    'MIN_IDS':2000,                 #样本最少ID数
    'MAX_IDS':2000,                 #样本最多ID数
    'MAX_DAYS':7,                 #爬取内容离今天最远天数
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

#缓存表
ids_queue=[Config['ENTRY_USERID']]
ids_history=[]
tb_users={}
weibo_total=0
tb_weibos={}

"""
保存爬取的数据为csv
"""
def ntdict2csv(filename,d,NT):
    with open(filename,'w',newline='') as f:
        fw =csv.writer(f)
        fw.writerow(NT._fields)
        for i in d.values():
            fw.writerow(i)
        f.close()

"""
从csv读取数据，转换成NamedTuple字典
"""
def csv2ntdict(filename,NT):
    d={}
    with open(filename) as f:
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
'id screen_name profile_image_url profile_url gender followers_count follow_count'
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
        js['user']['follow_count']
    )
    return user

"""
判断用户是否新的
"""
def isUserNeedToAdd(user):
    if(user.id in tb_users):
        return False
    if(user.followers_count<int(Config['MIN_FANS']) or user.followers_count>int(Config['MAX_FANS'])):
        return False
    return True

"""
获取某个用户ID的Follows
"""
def spiderId(userId):
    #print("userId==========",userId)
    #获取关注者列表
    url = Config['URL_FOLLOWS_FIRST'].format(userId)
    #print("url==========",url)

    """抓取关注列表第一页,计算分页数和全部关注的位置"""
    js = requests.get(url,headers=header).json()
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
        #print(url)
        while True:
            try:
                print('{}页开始========={}'.format(str(p),url))
                js = requests.get(url,headers=header).json()                
            except Exception as e:
                time.sleep(60)
            else:
                time.sleep(2)
                break
        #print("len(js['data']['cards'])====",len(js['data']['cards']))
        count=0
        for f in js['data']['cards'][-1]['card_group']:
            #print('f================',f)
            #print(f['user']['id'],'  :  ',f['user']['screen_name'],'  被粉数:  ',f['user']['followers_count'], '  粉人数:  ', f['user']['follow_count'])
            user =parseUser(f)
            if(isUserNeedToAdd(user)):
                tb_users[user.id]=user
                print('user{}|{}==========='.format(str(len(tb_users)),str(len(ids_queue))),user)
            #print('ids_queue===========',ids_queue)
            #print('ids_history===========',ids_history)
            if (user.id not in ids_queue) and (user.id not in ids_history):
                ids_queue.append(user.id)
                #print('user{}==========='.format(str(len(tb_users))),user)
            count+=1
            #spiderIds(user.id)
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
    print('已爬取用户=============',tb_users)
    ntdict2csv("./tb_users.csv",tb_users,User)

"""
解析微博信息
'itemid scheme created_at id text textLength userid reposts_count comments_count attitudes_count obj_ext'
"""
def parseWeibo(js):
    print('t=========',js)
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
    if(weibo.id in tb_weibos):
        return False
    if((datetime.now()- datetime.strptime(weibo.created_at,'%Y-%m-%d')).days<int(Config['MAX_DAYS'])):
        return False
    return True

"""
获取某个用户ID的Follows
"""
def spiderWeibo(userId):
    #print("userId==========",userId)
    #获取关注者列表
    url = Config['URL_WEIBO_FIRST'].format(userId)
    #print("url==========",url)

    """抓取关注列表第一页,计算分页数和全部关注的位置"""
    js = requests.get(url,headers=header).json()
    #print("==========js==========",js)
    total_weibos = js['data']['cardlistInfo']['total']
    weibo_total+=total_weibos
    #print("==========total_weibos==========",total_weibos)
    page_weibos = len(js['data']['cards'])
    #print("==========page_follows_number==========",page_follows_number)
    total_pages = total_weibos // page_weibos

    p=1
    while p<=total_pages:
        url = Config['URL_WEIBO_PAGE'].format(userId,str(p))
        #print(url)
        while True:
            try:
                print('{}页开始========={}'.format(str(p),url))
                js = requests.get(url,headers=header).json()                
            except Exception as e:
                time.sleep(60)
            else:
                time.sleep(2)
                break
        #print("len(js['data']['cards'])====",len(js['data']['cards']))
        count=0
        print(js['data']['cards'])
        for f in js['data']['cards']:
            #print('f================',f)
            if(f['card_type']!=9):
                continue
            weibo =parseWeibo(f)
            if(isWeiboNeedToAdd(weibo)):
                tb_weibos[weibo.id]=weibo
                print('weibo{}|{}==========='.format(str(len(tb_weibos)),str(weibo_total),weibo))
            count+=1
        p+=1

"""
获取符合条件的所有微博ID样本
"""
def spiderWeibos():
    for user in tb_users.values():
        spiderWeibo(user.id)
    print('已爬取微博=============',tb_weibos)
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
    #spiderIds()
    
    tb_users = csv2ntdict("./tb_users.csv",User)
    #print(tb_users)
    #ntdict2csv("./tb_users.csv",tb_users,User)

    spiderWeibos()
