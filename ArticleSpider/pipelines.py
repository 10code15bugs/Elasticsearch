# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import pymysql
from twisted.enterprise import adbapi
from scrapy.exporters import JsonItemExporter
#import pandas
import redis
redis_db =  redis.Redis(host='127.0.0.1',port=6379,db=1)

redis_data_dict = 'zl'
'''class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item'''

class JsonWithEncodingPipeline(object):
    #自定义json文件导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self,item,spider):
        lines=json.dumps(dict(item),ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()

class JsonExporterPipeline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file=open('articleexprt.json','wb')
        self.exporter=JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self,spider):
        self.file.close()
    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item

class MysqlPipelins(object):
    #同步插入 会堵塞

    def __init__(self):
        self.conn=pymysql.connect('localhost','root','634498','scrapy')#charset='utf-8',use_unicode=True)
        self.cursor=self.conn.cursor()
        redis_db.flushdb()   
        if redis_db.hlen(redis_data_dict) == 0:  # 判断redis数据库中的key，若不存在就读取mysql数据并临时保存在redis中
            sql = 'select url from boke'  # 查询表中的现有数据
            df = pandas.read_sql(sql,self.conn)  # 读取mysql中的数据
             # print(df)
            for url in df['url'].get_values():
                redis_db.hset(redis_data_dict,url,0)

    def process_item(self, item, spider):#增量爬取
    
        if redis_db.hexists(redis_data_dict,item['url']): # 比较的是redis_data_dict里面的field
            print("数据库已经存在该条数据，不再继续追加")
        else:
            self.do_insert(item)
    def do_insert(self, item):
        insert_sql='''insert into boke(title,date,url,front_image_url,url_object_id,front_image_path,content)
            VALUES(%s,%s,%s,%s,%s,%s,%s)'''
        item_sql=(item['title'],item['date'], item['url'],
                       item['front_image_url'],item['url_object_id'],item['front_image_path'],item['content'])
        self.cursor.execute(insert_sql,item_sql)
        self.conn.commit()
        return item


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print('----------录入错误------------')
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)



class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        global image_file_path
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item

class ElasticsearchPipeline(object):
    #将数据写入到es中

    def process_item(self, item, spider):
        #将item转换为es的数据
        item.save_to_es()

        return item

