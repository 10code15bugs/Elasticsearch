# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import scrapy
import redis
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader
import re
from ArticleSpider.utils.common import extract_num
from .settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT

from ArticleSpider.models.es_types import ArticleType,QuestionType,AnswerType,LagouType,MovieType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

redis_cli=redis.StrictRedis()

def add_boke(value):
    return value+"-ccc"


def get_nums(value):
    match_re=re.match('.*?(\d+).*',value)
    if match_re:
        nums=int(match_re.group(1))
    else:
        nums = 0
    return nums


def add_date(value):
    match_re = re.match(r'.*?((\d+).(\d+).(\d+))', value)
    if match_re:
        date = match_re.group(1)
    return date

def remove_comment_tags(value):

    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value
def return_value(value):#覆盖掉TakeFirst()
    return value

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
            used_words = used_words | new_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
            used_words.update(new_words)

    return suggests



class ArticleItemLoader(ItemLoader):
    #自定义itemloder，list转换成str
    default_output_processor = TakeFirst()


class ArticleSpiderItem(scrapy.Item):

    title = scrapy.Field()
        #input_processor=MapCompose(lambda x:x+'-aaa',add_boke)


    date = scrapy.Field(
        input_processor=MapCompose(add_date)
    )
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    front_image_url=scrapy.Field(
        output_processor=MapCompose(return_value)
    )#这个字段必须以list传递给下载器，return_value函数覆盖TakeFirst()
    front_image_path = scrapy.Field()
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = "insert into boke(title,date,url,front_image_url,url_object_id,front_image_path,content)VALUES(%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE content=VALUES(content),date=VALUES(date)"
        params=(self['title'], self['date'], self['url'],self['front_image_url'],
                self['url_object_id'], self['front_image_path'], self['content'])
        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.date = self["date"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        #article.praise_nums = self["praise_nums"]
       # article.fav_nums = self["fav_nums"]
       # article.comment_nums = self["comment_nums"]
        article.url = self["url"]

        article.meta.id = self["url_object_id"]

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.date, 7)))

        article.save()

        redis_cli.incr("cnblogs_count")

        return
'''class ArticleSpiderItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    front_image_url=scrapy.Field()
    front_image_path = scrapy.Field()
    content = scrapy.Field()'''
class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = "insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)"
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = self["watch_user_num"][0]
            click_num = self["watch_user_num"][1]
        else:
            watch_user_num = self["watch_user_num"][0]
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)

        return insert_sql,params

    def save_to_es(self):
        question = QuestionType()
        question.title = "".join(self["title"])
        question.topics = ",".join(self["topics"])

        #question.crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        question.url = self["url"][0]
        question.zhihu_id = self["zhihu_id"][0]
        question.answer_num = extract_num("".join(self["answer_num"]))
        question.comment_nums = extract_num("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            question.watch_user_num = self["watch_user_num"][0]
            question.click_num = self["watch_user_num"][1]
        else:
            question.watch_user_num = self["watch_user_num"][0]
            question.click_num = 0
        question.content = remove_tags("".join(self["content"]))



        question.suggest = gen_suggests(QuestionType._doc_type.index, ((question.title, 10), (question.topics, 7)))

        question.save()

        redis_cli.incr("zhihu_count")

        return
class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    created_time = scrapy.Field()
    updated_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = "insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,created_time, updated_time, crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),updated_time=VALUES(updated_time)"

        created_time = datetime.datetime.fromtimestamp(self["created_time"])
        updated_time = datetime.datetime.fromtimestamp(self["updated_time"])
        params = (
            self["zhihu_id"],self["url"],self["question_id"],self["author_id"],self["content"],self["praise_num"],self["comments_num"],created_time,updated_time,self["crawl_time"]
        )

        return insert_sql, params

    def save_to_es(self):
        answer = AnswerType()
        #question.crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        answer.url = self["url"]
        answer.zhihu_id = self["zhihu_id"]
        answer.question_id = self["question_id"]
        answer.author_id = self["author_id"]

        answer.praise_num = self["praise_num"]
        answer.comments_num = self["comments_num"]
        answer.content = remove_tags("".join(self["content"]))
        answer.suggest = gen_suggests(AnswerType._doc_type.index, ((answer.content, 10), (answer.author_id, 7)))

        answer.save()

        redis_cli.incr("zhihu_count")

        return

def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)

class LagouJobItemLoader(ItemLoader):

    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql ="insert into lagou_job(a,url,url_object_id,salary,job_city,work_years,degree_need,job_type,publish_time,tags,job_advantage,job_desc,job_addr,company_url,company_name,crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)"
        #insert_sql ="insert into lagou_job(url, url_object_id,title,salary, job_city, work_years, degree_nedd,job_type, publish_time,tags,job_advantage, job_desc, job_addr, company_url, company_name,crawl_time)
                     #" VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)"

        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["tags"],self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["crawl_time"],
        )

        return insert_sql, params

    def save_to_es(self):
        lagouw = LagouType()
        lagouw.title = self["title"]
        lagouw.url = self["url"]
        #lagouw.url_object_id = self["url_object_id"]
        lagouw.salary = self["salary"]
        lagouw.job_city = self["job_city"]
        lagouw.work_years = self["work_years"]
        lagouw.degree_need = self["degree_need"]
        lagouw.job_type = self["job_type"]
        lagouw.publish_time = self["publish_time"]
        lagouw.job_advantage = self["job_advantage"]
        lagouw.job_desc = self["job_desc"]
        lagouw.job_addr = self["job_addr"]
        lagouw.company_name = self["company_name"]
        lagouw.company_url = self["company_url"]
        lagouw.tags = self["tags"]

        lagouw.suggest = gen_suggests(LagouType._doc_type.index, ((lagouw.title, 10), (lagouw.job_desc, 7)))

        lagouw.save()

        redis_cli.incr("lagou_count")

        return



class YdDyItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    type_movie = scrapy.Field()
    grade = scrapy.Field()
    content = scrapy.Field()
    urldownload = scrapy.Field( )
    def save_to_es(self):
        movie = MovieType()
        movie.title = self["title"]
        movie.url = self["url"]
        movie.url_object_id = self["url_object_id"]
        movie.type_movie = self["type_movie"]
        movie.grade = self["grade"]
        movie.content = self["content"]
        movie.urldownload = self["urldownload"]
        movie.suggest = gen_suggests(LagouType._doc_type.index, ((movie.title, 10), (movie.type_movie, 7)))

        movie.save()

        redis_cli.incr("moviee_count")

        return