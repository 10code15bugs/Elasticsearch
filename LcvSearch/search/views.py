import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType,QuestionType,AnswerType,LagouType,MovieType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis(host='127.0.0.1',charset='utf-8',decode_responses=True)
# Create your views here.
#def suggest(request):
class IndexView(View):
    #首页
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"topn_search":topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        s_type = request.GET.get("s_type", "")

        re_datas = []
        if key_words:
            if s_type == "article":

                s = ArticleType.search()
                s = s.suggest('my_suggest', key_words, completion={
                    "field": "suggest", "fuzzy": {
                        "fuzziness": 2
                    },
                    "size": 10
                })
            elif s_type == "question":

                s = QuestionType.search()
                s = s.suggest('my_suggest', key_words, completion={
                    "field": "suggest", "fuzzy": {
                        "fuzziness": 2
                    },
                    "size": 10
                })
            elif s_type == "job":

                s = LagouType.search()
                s = s.suggest('my_suggest', key_words, completion={
                    "field": "suggest", "fuzzy": {
                        "fuzziness": 2
                    },
                    "size": 10
                })
            elif s_type == "moviee":

                s = MovieType.search()
                s = s.suggest('my_suggest', key_words, completion={
                    "field": "suggest", "fuzzy": {
                        "fuzziness": 2
                    },
                    "size": 10
                })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas),content_type="application/json")




class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q","")
        s_type = request.GET.get("s_type", "article")

        redis_cli.zincrby("search_keywords_set", 1,key_words)
        # 搜索关键词加1操作#返回最高次数
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1
        zhihu_count = redis_cli.get("zhihu_count")  # 爬取量
        cnblogs_count = redis_cli.get("cnblogs_count")
        lagou_count = redis_cli.get("lagou_count")
        movie_count = redis_cli.get("movie_count")
        start_time = datetime.now()
        if s_type == "article":
            response = client.search(
                index="jobbole",
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["title", "content"]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {

                            "title": {},
                            "content": {},
                        }
                    }
                })
        elif s_type == "question":

            response = client.search(
                index="zhihuquestion",
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["topics", "title","content"]
                        }
                    },

                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "topics": {},
                            "title": {},
                            "content": {},
                        }
                    }
                })
        elif s_type == "job":
            response = client.search(
                index="lagou",
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["tags", "title", "job_desc"]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {

                            "tags": {},
                            "title": {},
                            "job_desc": {},
                        }
                    }
                })
        elif s_type == "moviee":
            response = client.search(
                index="ygdyy",
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["type_movie", "title", "content"]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {

                            "type_movie": {},
                            "title": {},
                            "content": {},
                        }
                    }
                })



        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10) > 0:
            page_nums = int(total_nums/10) +1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                if "title" in hit["_source"]:
                    hit_dict["title"] = hit["_source"]["title"]
                else:
                    pass

            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            elif "content" in hit["_source"]:
                hit_dict["content"] = hit["_source"]["content"][:500]
            elif "job_desc" in hit["_source"]:
                hit_dict["job_desc"] = hit["_source"]["job_desc"][:150].replace('\n','')
            else:
                pass
            if "date" in hit["_source"]:
                hit_dict["date"] = hit["_source"]["date"]
            elif "publish_time" in hit["_source"]:
                hit_dict["publish_time"] = hit["_source"]["publish_time"]
            else:
                pass
            if "salary" in hit["_source"]:
                hit_dict["salary"] = hit["_source"]["salary"]
            else:
                pass
            if "job_city" in hit["_source"]:
                hit_dict["job_city"] = hit["_source"]["job_city"]
            else:
                pass
            if "work_years" in hit["_source"]:
                hit_dict["work_years"] = hit["_source"]["work_years"]
            else:
                pass
            if "degree_need" in hit["_source"]:
                hit_dict["degree_need"] = hit["_source"]["degree_need"]
            else:
                pass
            if "click_num" in hit["_source"]:
                hit_dict["click_num"] = hit["_source"]["click_num"]
            else:
                pass
            if "watch_user_num" in hit["_source"]:
                hit_dict["watch_user_num"] = hit["_source"]["watch_user_num"]
            else:
                pass
            if "answer_num" in hit["_source"]:
                hit_dict["answer_num"] = hit["_source"]["answer_num"]
            else:
                pass
            if "comment_nums" in hit["_source"]:
                hit_dict["comment_nums"] = hit["_source"]["comment_nums"]
            else:
                pass
            #if "question_id" in hit["_source"]:
               # hit_dict["question_id"] = hit["_source"]["question_id"]
            #else:
               # pass
            #if "praise_num" in hit["_source"]:
               # hit_dict["praise_num"] = hit["_source"]["praise_num"]
            #else:
               # pass
            if "type_movie" in hit["_source"]:
                hit_dict["type_movie"] = hit["_source"]["type_movie"]
            else:
                pass
            if "grade" in hit["_source"]:
                hit_dict["grade"] = hit["_source"]["grade"]
            else:
                pass
            if "urldownload" in hit["_source"]:
                hit_dict["urldownload"] = hit["_source"]["urldownload"]
            else:
                pass
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page":page,
                                              "all_hits":hit_list,
                                              "s_type":s_type,
                                              "key_words":key_words,
                                              "total_nums":total_nums,
                                              "page_nums":page_nums,
                                              "last_seconds":last_seconds,
                                              "zhihu_count":zhihu_count,
                                              "cnblogs_count": cnblogs_count,
                                               "lagou_count":lagou_count,
                                               "movie_count":movie_count,
                                              "topn_search":topn_search})



