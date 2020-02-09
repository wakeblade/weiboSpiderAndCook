#!/usr/bin/env python
# coding: utf-8

"""
 案例名： 基于nltk的微博热点趋势大数据分析

 在本次案例中，我们首先需要载入通过爬虫程序抓取的微博文本内容，然后使用结巴分词对每个博主的微博进行分词处理，然后汇总每个博主的分词获得总词袋，再计算总词袋中词汇的每日文档频率（视每个博主每天所有微博为一个文档）。这样我们可以获得每一天微博热点词汇的排行。

 数据分析的展开，我们又分成三个步骤：
 
 第一步，我们需要累加30日内所有热点词的每日文档频率，获得热点词的30日总文档频率。
 
 第二步，我们需要选取出top20的热点词，然后把这些top20热点词的每天的文档频率做为一行，添加日期属性后，合并成一个DataFrame。
 
 第三步，我们需要利用matplotlib画出这个Dataframe中top20热点词的文档频率的变化趋势曲线图。
 
 通过这个曲线图，我们可以清晰地看到，近30日内公众在的微博中关注的热点从出现，到发酵，到热议，到降温，到遗忘的整个过程。

################################################
#   用到的Python 库:
# * [NumPy](http://www.numpy.org/)
# * [Pandas](http://pandas.pydata.org/)
# * [jieba](https://pypi.org/project/jieba/)
# * [Matplotlib](http://matplotlib.org/)
"""

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

# ### 数据准备

df = pd.read_csv("./tb_weibos.csv",usecols=['userid','created_at','text'],parse_dates = ['created_at']) 
# #### 2）先查看一下前10条数据: 
df.head(10)


# 把每天每个博主发布的微博合并成一个文档。然后使用结巴分词，并且过滤掉无意义的停用词</b>

import jieba
import jieba.analyse

#载入停用词
jieba.analyse.set_stop_words('stopwords.txt')

def documentwords(value):
    text = ','.join(value.astype(str).tolist())
    words = jieba.analyse.extract_tags(text, topK=10, withWeight=False)
    #words = jieba.analyse.extract_tags(text,50)
    #words = jieba.cut(text,cut_all=False,HMM=False)
    #words = jieba.lcut(text,cut_all=False)
    return set(words)

documents = [(index[0],index[1],documentwords(value)) for index,value in df.groupby(['created_at','userid'])['text']]
documents = pd.DataFrame(columns=['created_at','userid','words'],data=documents)
documents.head()

# <b>对总词袋的每个词汇计算每日文档频率，每个博主每天所有的微博视为一个文档（为什么？）</b>
from collections import Counter

def daywords(value):
    result =[]
    for words in value:
        result.extend(list(words))
    return Counter(result).most_common(10000)

daywords = [(index,word,count) for index,value in documents.groupby('created_at')['words'] for word,count in daywords(value)]
daywordCounts = pd.DataFrame(columns=['created_at','word','count'],data=daywords)
daywordCounts.sort_values(['created_at','count'],ascending=[True,False],inplace=True)
#daywordCounts

# <b>对每日文档频率取TOP2，汇总成热点词。然后为热点词日词频建立时间序列</b>
hotwordCounts = daywordCounts.groupby(['created_at']).head(2)
days = hotwordCounts['created_at'].unique()
hotwords = hotwordCounts.sort_values(['created_at','count'],ascending=[False,False])['word'].unique()
wordCounts = pd.DataFrame(index=days,columns=hotwords)
for hotword in hotwords:
    value = daywordCounts[daywordCounts.word==hotword][['created_at','count']]
    value.set_index('created_at',inplace=True)
    #print(value)
    wordCounts[hotword] = value
wordCounts.fillna(1,inplace=True)
#wordCounts

# <b>利用Matplotlib画出这TOP20热点词的日文档频率的变化曲线，分析理解其意义</b>
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
import random
import scipy.interpolate
from scipy.interpolate import interp1d
import numpy as np
import talib

# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.figure(figsize=(12,8), dpi=180)
plt.subplot(1,1,1)
markers=".,ov^<>1234sp*hH+xDd|_"
count = len(markers)-1
for hotword in hotwords:
    x = wordCounts.index
    y = wordCounts[hotword]
    #y = wordCounts[hotword].rolling(2).mean()
    #y = talib.EMA(wordCounts[hotword],2)

    #plt.plot(values.index,y,marker=markers[count%len(markers)],label=hotword)
    #plt.plot(wordCounts.index,wordCounts[hotword],marker=random.choice(markers),label=hotword)
    plt.plot(x,y,marker=markers[count%len(markers)],label=hotword)
    #plt.plot(x,y,marker=random.choice(markers),label=hotword)
    #plt.plot(x,y,label=hotword)
    count-=1

    """
    x = np.array([i for i in range(len(values.index))])
    print(f"x({len(x)})={x}")
    y = np.array(values['count'])
    print(f"y({len(y)})={y}")
    func = interp1d(x, y, kind = 'cubic')
    xx = np.linspace(x.min(),x.max(),30) 
    plt.plot(xx,func(xx),marker=random.choice(markers),label=str(index))
    """
    plt.xticks(rotation=60)
plt.legend() # 显示图例
plt.show()