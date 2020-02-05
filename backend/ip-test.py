import requests
import queue
import threading
from lxml import etree
 
#要爬取的URL
#url = "http://"+str(time.localtime().tm_year)+".ip138.com/ic.asp"
#url = 'https://httpbin.org/ip'
#url = "http://ip.chinaz.com/getip.aspx"
#url = "http://m.weibo.cn"
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

#代理ip网站
proxy_url = "https://www.kuaidaili.com/free/inha/{page}/"
 
class MyThreadPool:
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self._pool = queue.Queue(maxsize)
        for _ in range(maxsize):
            self._pool.put(threading.Thread)
 
    def get_thread(self):
        return self._pool.get()
 
    def add_thread(self):
        self._pool.put(threading.Thread)
 
 
def get_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               }
    response = requests.get(url,headers=headers)
    html_str = response.text
    return html_str
 
 
def proxy_get_url(url,prox):
    proxies = {}
    proxies["http"] = prox
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               }
    response = requests.get(url,headers=headers,proxies=proxies,timeout=3)
    html_str = response.text
    return html_str
 
def ip_proxy(html_str):
    html = etree.HTML(html_str)
    ip_list = html.xpath('//tr/td[@data-title="IP"]/text()')
    port_list = html.xpath('//tr/td[@data-title="PORT"]/text()')
    http_list = []
    for i in range(len(ip_list)):
        http_proxy = ip_list[i]+":"+port_list[i]
        http_list.append(http_proxy)
    return http_list
 
 
def available_ip(ip_list):
    for ip in ip_list:
        try:
            proxy_get_url('https://www.baidu.com/',ip)
        except Exception as e:
            continue
        IP_LIST.append(ip)
  
if __name__ == "__main__":
    IP_LIST = []
    with open('./ips.txt') as f:
        IP_LIST = [line.split('@')[0] for line in f]

    pool = MyThreadPool(20) #线程池数
    #验证代理ip
    for i in range(1,20): #页数
        page_ip = get_url(proxy_url.format(page=i))
        ip_list = ip_proxy(page_ip)
        t = pool.get_thread()
        obj = t(target=available_ip,args=(ip_list,))
        obj.start()

    valid_ips=[]
    for ip in IP_LIST:
        print(ip)
        try:
            response = requests.get(url,proxies={'https':ip,'http':ip},headers=header,timeout=(2,2))
            print('response : ',response.text)
            valid_ips.append(ip)
        except Exception as e:
            continue
    print('#'*40)
    for ip in valid_ips:
        print(ip)