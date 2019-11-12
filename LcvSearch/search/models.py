from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["127.0.0.1"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    #伯乐在线文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "jobbole"
        doc_type = "article"

class QuestionType(DocType):
    #zhihu
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    topics=Text(analyzer="ik_max_word")
    #crawl_time = Date()
    url = Keyword()
    zhihu_id = Integer()
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Keyword()
    click_num= Keyword()
    content = Text(analyzer="ik_max_word")




    class Meta:
        index = "zhihuquestion"
        doc_type = "question"

class AnswerType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    created_time = Date()
    updated_time = Date()
    crawl_time = Date()
    url = Keyword()
    zhihu_id = Integer()
    question_id = Integer()
    author_id = Keyword()
    praise_num = Integer()
    comments_num = Integer()
    content = Text(analyzer="ik_max_word")
    class Meta:
        index = "zhihuanswer"
        doc_type = "question"

class LagouType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title=Text(analyzer="ik_max_word")
    url = Keyword()
    #url_object_id=Integer()
    salary=Keyword()
    job_city=Keyword()
    work_years=Keyword()
    degree_need =Keyword()
    job_type=Keyword()
    publish_time = Keyword()
    job_advantage = Keyword()
    job_desc=Text(analyzer="ik_max_word")
    job_addr=Keyword()
    company_name=Keyword()
    company_url=Keyword()
    tags=Text(analyzer="ik_max_word")

    class Meta:
        index = "lagou"
        doc_type = "job"
class MovieType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id=Keyword()
    type_movie = Text(analyzer="ik_max_word")
    grade = Keyword()
    content = Text(analyzer="ik_max_word")
    urldownload = Keyword()
    class Meta:
        index = "ygdyy"
        doc_type = "moviee"
if __name__ == "__main__":
    ArticleType.init()
