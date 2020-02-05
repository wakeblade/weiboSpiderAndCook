import csv
import collections
import ast

Follow = collections.namedtuple('Follow','id follows')

tb_follows = {'1222967455': ['6528866809', '2714280233', '1170980471', '1856206461', '2238285583', '2474984322', '1229587265', '1878923963', '1810632930', '5696365228', '1614037520', '2382064902', '1151243311', '1664180272']}

"""
保存字典数据为csv
"""
def dict2csv(filename,m,d):
    with open(filename,m,encoding='UTF-8',newline='') as f:
        fw =csv.writer(f)
        #fw.writerow(['id','follows'])
        for k,v in d.items():
            fw.writerow([k,v])
        f.close()

"""
从csv读取字典数据
"""
def csv2dict(filename):
    d={}
    with open(filename,'r',encoding='UTF-8') as f:
        fr =csv.reader(f)
        for i in fr:
            if(len(i)>0):
                d[i[0]]=ast.literal_eval(i[1])
        f.close()
    return d

dict2csv("./tb_follows.csv",'w+',tb_follows)
tb_follows= csv2dict("./tb_follows.csv")