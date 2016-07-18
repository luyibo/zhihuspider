#coding=utf-8
__author__ = 'lyb-mac'
import time
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.selector import Selector
from zhihu.items import AuthorItem
from scrapy.http import Request,FormRequest
from PIL import Image
import json
from scrapy.contrib.linkextractors import LinkExtractor
from bs4 import BeautifulSoup as bs
from scrapy.xlib.tx._newclient import HTTPClientParser, ParseError
import requests

class Authorspider(CrawlSpider):
    name = 'author'
    allow_domains = []
    start_urls = ["https://www.zhihu.com/"]
    headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8    "Accept-Encoding": "gzip,deflate"',
    "Referer": "https://www.zhihu.com/",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
'Cache-Control':'max-age=0',

    }

    rules = (
        Rule(LinkExtractor(allow = (r'/question/\d+', )),  follow = True),
        Rule(LinkExtractor(allow=(r'/people/(\w+-?)+$')),callback='parse_item'),
    )

    def start_requests(self):
       return [Request( 'https://www.zhihu.com/login/email',
                       headers = self.headers,
                       meta = {'cookiejar':1},
                       callback = self.get_captcha )]

    def get_captcha(self,response):
        sel = Selector(response)
        print response.meta['cookiejar']
        self.xsrf = sel.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        t = str(int(time.time()*1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login'
        print captcha_url
        return [Request(url=captcha_url,
                       headers=self.headers,
                       meta={'cookiejar':response.meta['cookiejar'],
                             "_xsrf": self.xsrf},
                       callback=self.login)]


    def login(self,response):
        with open('captcha.png','w') as f:
            f.write(response.body)
            f.close()
        im = Image.open('captcha.png')
        im.show()
        captcha = raw_input('please:')
        return [FormRequest("https://www.zhihu.com/login/email",
                        meta = {'cookiejar':response.meta['cookiejar'],
                                '_xsrf':response.meta['_xsrf']},
                        headers = self.headers,
                        formdata = {
                            '_xsrf' : response.meta['_xsrf'],
                            'email' : '1428260548@qq.com',
                            'password' : 'luyibo',
                            'remember_me' : 'true',
                            "captcha": captcha,
                        },
                        callback=self.after_login,
                            dont_filter=True)]

    def after_login(self, response):
        print response.body
        return [Request('https://www.zhihu.com/',
                       headers = self.headers,
                       meta = {'cookiejar':response.meta['cookiejar']},
                       callback = self.parse,
                       dont_filter=True)]

    def parse_item(self,response):
        sel = Selector(response)
        item = AuthorItem()
        name = sel.xpath("//div[@class='title-section ellipsis']/span[@class='name']/text()").extract()
        agree = sel.xpath("//span[@class='zm-profile-header-user-agree']/strong/text()").extract()
        followers = sel.xpath("//a[@class='item'][2]/strong/text()").extract()
        item['name'] = name
        item['agree'] = agree
        item['followers'] = followers
        yield item
