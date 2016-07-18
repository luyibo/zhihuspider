__author__ = 'lyb-mac'

import requests
from bs4 import BeautifulSoup as bs
import re
import MySQLdb
import urllib2
class proxyspider():
    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost',user='root',passwd='password',db='text',port=3306)
        self.cur=self.conn.cursor()
        self.s = requests.session()
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17',
                       'Referer':'https://www.zhihu.com/',}
        self.url = 'http://www.xicidaili.com/nn/'

    def get_proxy(self):
        r = self.s.get(self.url,headers=self.header).content
        all1 = bs(r,'lxml').find_all('tr',class_='odd')
        all2 = bs(r,'lxml').find_all('tr',class_='')
        for i in all1:
            ip1 = i.find_all('td',class_=None)[0].string
            port1 = i.find_all('td',class_=None)[1].string
            proxy_host ="http://"+ip1+':'+port1
            print proxy_host
            try:
                c = self.s.get(url='http://www.ip138.com',headers=self.header,proxies={'http':proxy_host},timeout=1).status_code
                if c==200:
                    print '1'
                    try:
                        self.cur.execute('insert into proxyip(ip,port) VALUES(%s,%s)',(ip1,port1))
                    except Exception,e:
                        print 'd'
                        continue

            except Exception,e:
                print 'fail'
                continue
        for j in all2:
            if j.find_all('td',class_=None):
                ip2 = j.find_all('td',class_=None)[0].string
                port2 = j.find_all('td',class_=None)[1].string
                proxy_host ="http://"+ip2+':'+port2
                print '2:'+proxy_host
                try:
                    if self.s.get('http://www.ip138.com',proxies={'http':proxy_host},timeout=1).status_code==200:
                        print '2'
                        try:
                            self.cur.execute('insert into proxyip(ip,port) VALUES(%s,%s)',(ip2,port2))
                        except Exception,e:
                            print 'd'
                            continue
                except Exception,e:
                    print 'fail'
                    continue
    def main(self):
        for i in range(1,10):
            self.url = self.url +'%d'%i
            print self.url

            self.get_proxy()
            self.url =  'http://www.xicidaili.com/nn/'
        self.cur.close()
        self.conn.commit()
        self.conn.close()

pro = proxyspider()
pro.main()
