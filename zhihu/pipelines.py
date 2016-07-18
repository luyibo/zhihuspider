# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings
import json
import codecs
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class ZhihuPipeline(object):
    '''def __init__(self):
        self.client = pymongo.MongoClient(settings['MONGODB_SERVER'],settings['MONGODB_PORT'])
        self.db = self.client[settings['MONGODB_DB']]
        self.col = self.db[settings['MONGODB_COLLECTION']]

    def process_item(self,item,spider):
        for i in item['title']:
            if self.col.find({'title':i}).count()<1:
                zhihu = {
                    'title':i,
                }
                self.col.insert(zhihu)'''
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            'MySQLdb',
            db = 'text',
            user = 'root',
            passwd = 'password',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8mb4',
            use_unicode = True
        )

    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self,tx,item):
            for i in range(len(item['title'])):
                    tx.execute('INSERT INTO zhihu(title,author,vote,answer) values(%s,%s,%s,%s)',(item['title'][i],item['name'][i],item['vote'][i],item['answer'][i]))

'''class AuthorPipeline(object):

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            'MySQLdb',
            db = 'text',
            user = 'root',
            passwd = 'password',
            cursorclass = MySQLdb.cursors.DictCursor,
            charset = 'utf8mb4',
            use_unicode = True
        )

    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self,tx,item):
        if item['name']:
                tx.execute('INSERT INTO author(name,followers,agree) values(%s,%s,%s)',(item['name'],item['followers'],item['agree']))'''



