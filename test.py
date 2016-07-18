#coding=utf-8
__author__ = 'lyb-mac'
import re
import time
pattern1 = '27539055/answer'
pattern2 = 'abcd123'
from bs4 import BeautifulSoup as bs

import pytesseract
from PIL import Image

import requests
s = requests.session()
'''header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17',
                       'Referer':'https://www.zhihu.com/',}
r = s.get('http://www.xicidaili.com/nn/',headers=header).content
all1 = bs(r,'lxml').find_all('tr',class_='')
print type(all1[1].find_all('td',class_=None)[0].string)'''

import MySQLdb

conn = MySQLdb.connect(host="localhost",user="root",passwd="password",db="text")
cur = conn.cursor()
cur.execute('select ip,port from proxyip')
cds=cur.fetchall()
for i in cds:
    print '{"ip_port":'+"'"+i[0]+':'+i[1]+"'"+", 'user_pass': ''},"+'\n'

'''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df  = pd.DataFrame(np.random.randn(6,4),columns=list('ABCD'),index=range(1,7))
print df.describe()'''

'''im = Image.open('aa.tif')
im = im.convert('L')
code = pytesseract.image_to_string(im)
print code'''
