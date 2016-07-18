# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()  #保存抓取问题的url
    title = scrapy.Field()  #抓取问题的标题
    vote = scrapy.Field()  #抓取问题的描述
    answer = scrapy.Field()  #抓取问题的答案

class AuthorItem(scrapy.Item):
    name = scrapy.Field()
    agree = scrapy.Field()
    followers = scrapy.Field()