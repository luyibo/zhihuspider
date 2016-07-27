__author__ = 'lyb-mac'
import time
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.selector import Selector
from zhihu.items import ZhihuItem
from scrapy.http import Request,FormRequest
from PIL import Image
import json
from scrapy.contrib.linkextractors import LinkExtractor
from bs4 import BeautifulSoup as bs
import re

class zhihuspider(CrawlSpider):
    name = 'zhihu'
    allow_domains = ['zhihu.com']
    start_urls = ["https://www.zhihu.com/topic/19595689/hot"]
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
    "Connection": "keep-alive",
    "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17",
    "Referer": "http://www.zhihu.com/",
    "Cookie":'q_c1=f71307079df9462993709f3ac0fcf194|1467246979000|1467246979000; d_c0="ABCAq7bCJwqPTmxQkiLwZp_nO9VpWrUMU1k=|1467246980"; _zap=85fbee53-bd97-4e82-b8fe-4ce7f4da3f4a; _za=088a0d63-1514-49b7-96db-b9a731783dda; _xsrf=ab6c126d1b4d2a5f3e8e6d8b1c7afabd; l_n_c=1; l_cap_id="Yzc5OTNiMDE2OTYxNDEyOThhMTdhYTNkNWY4NjY0YTA=|1468283591|81ac927c9e504989367be728f04d5ccc19e675de"; cap_id="ZjcyNDI2OWRkZGQ5NDdjYTlkMmQ1NDA2MTNlYjRhM2U=|1468283591|8bb2cf1802a7979227f6f217395d7950f97a82a3"; __utmt=1; __utma=51854390.344106416.1468063895.1468155480.1468283593.8; __utmb=51854390.2.10.1468283593; __utmc=51854390; __utmz=51854390.1468063895.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/23241537/answer/76261620; __utmv=51854390.000--|2=registration_date=20130830=1^3=entry_date=20160630=1; login="MTA3YzQ1MGQ5NmEzNDBlYTg5ODQ5NjA3Mjg1ZDc2MDc=|1468283605|e30ce3059b5e9cb62b3ec44290f1e46e0e87162d"; z_c0=Mi4wQUFDQV9xWWRBQUFBRUlDcnRzSW5DaGNBQUFCaEFsVk4xY2VyVndBRmQxcEw0aFc0eVdSc2RfR2NrajJRcnROczJ3|1468283605|0cefe9fc7546a9ba4dee82826a0b0adf974c0e2e; a_t="2.0AACA_qYdAAAXAAAA1cerVwAAgP6mHQAAABCAq7bCJwoXAAAAYQJVTdXHq1cABXdaS-IVuMlkbHfxnJI9kK7TbNtQnIgQTXEAqoc2G--_mShc1lVgXw=="'

    }
    offset = 20


    def start_requests(self):
       return [Request( 'https://www.zhihu.com/login/email',
                       headers = self.headers,
                       meta = {'cookiejar':1},
                       callback = self.get_captcha )]

    def get_captcha(self,response):
        sel = Selector(response)
        self.xsrf = sel.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=1467249038299&type=login'
        return [Request(url=captcha_url,
                       headers=self.headers,
                       meta={'cookiejar':response.meta['cookiejar'],
                             "_xsrf": self.xsrf},
                       callback=self.login)]


    def login(self,response):
        with open('captcha.gif','w') as f:
            f.write(response.body)
            f.close()
        im = Image.open('captcha.gif')
        im.show()
        captcha = raw_input('please:')

        return [FormRequest("https://www.zhihu.com/login/email",
                        meta = {'cookiejar':response.meta['cookiejar'],
                                '_xsrf':response.meta['_xsrf']},
                        headers = self.headers,
                        formdata = {
                            '_xsrf' : response.meta['_xsrf'],
                            'email' : '*****',
                            'password' : '***',
                            'remember_me' : 'true',
                            "captcha": captcha,
                        },
                        callback=self.get_html)]


    def get_html(self, response):
        return [Request(url = "https://www.zhihu.com",
                            headers = self.headers,
                            meta = {
                                    "cookiejar": response.meta["cookiejar"],
                                    '_xsrf' : response.meta['_xsrf'],
                                },
                            dont_filter = True,
                        callback=self.parse_age)]

    def parse_age(self, response):
        problem = Selector(response)
        item = ZhihuItem()
        item['title'] = problem.xpath("//div[@class='feed-main']/div[@class='feed-content']/h2/a[@class='question_link']/text()").extract()
        start = problem.xpath("//div[@id='zh-question-list']/div[@id='js-home-feed-list']/div/@id").extract()[-1]
        yield item
        dic = {}
        dic["offset"] = 20
        dic["start"] = start[5:]
        data = {'method':'next','_xsrf':self.xsrf}
        p = json.dumps(dic)
        data["params"] = p
        yield FormRequest(url='https://www.zhihu.com/node/HomeFeedListV2',
                          headers=self.headers,
                          formdata=data,
                          meta={'cookiejar':response.meta['cookiejar']},
                          callback=self.get_next,
                         )

    def get_next(self,response):
        item = ZhihuItem()
        dic = {}
        t = []
        n = []
        v = []
        a = []
        for each in json.loads(response.body)['msg']:
            each = bs(each,'lxml')
            title = each.find('h2').string
            answer = each.find('textarea')
            name = each.find('div',class_='zm-item-answer-author-info')
            vote = each.find('a',class_='zm-item-vote-count')
            if title==None:break
            if answer:
                        answer = answer.string
                        answer = re.sub('<br>','\n',answer)
                        answer = re.sub('<p>|</p>','',answer)
                        answer = re.sub('<b>|</b>','',answer)
                        answer = re.sub('<li>|</li>','\t',answer)
                        answer = re.sub('<a .*?>|</a>','',answer)
                        answer =re.sub('<blockquote>|</blockquote>','',answer)
                        answer = re.sub('<u>|</u>','',answer)
                        answer = re.sub('<i .*?>|</i>','',answer)
                        answer = re.sub('<ul>|</ul>','',answer)
            else:answer = 'None'

            if name:
                if name.a:
                    name = name.a.string
                else: name = name.span.string
            else:
                name = each.find('div',class_="feed-source").a.string

            if vote:
                vote = vote.string
            else: vote = 'None'

            n.append(name)
            t.append(title)
            v.append(vote)
            a.append(answer)

            temp = each.find('div',class_='feed-item').get('id')
            if temp:
                self.start = temp
        item['title'] = t
        item['name'] = n
        item['answer'] = a
        item['vote'] = v
        yield item
        dic["offset"] = self.offset
        dic["start"] = self.start[5:]
        data = {'method':'next','_xsrf':self.xsrf}
        p = json.dumps(dic)
        data["params"] = p
        self.offset +=20
        yield FormRequest(url='https://www.zhihu.com/node/HomeFeedListV2',
                                  headers=self.headers,
                                  formdata=data,
                                  meta={'cookiejar':response.meta['cookiejar']},
                                  callback=self.get_next,
                         )

