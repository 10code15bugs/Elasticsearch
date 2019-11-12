import scrapy

import os
import bs4
import datetime
import pickle
import time

from ArticleSpider.utils.common import get_md5
import re
from ArticleSpider.items import YdDyItem
from ArticleSpider.settings import BASE_DIR
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
class MovieCrawler(RedisCrawlSpider):
    name = 'movie'
    redis_key = 'movie:start_urls'
    allowed_domains = ['www.ygdy8.com']
    #start_urls = ['https://www.ygdy8.com/']

    headers = {
        "HOST": "www.ygdy8.com",
        "Referer": "https://www.ygdy8.com/",
        # "USER_AGENT" : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'

    }
    rules = (
        #Rule(LinkExtractor(allow=("html/gndy/china/(.*).html",)), follow=True),

        Rule(LinkExtractor(allow=("html/gndy/rihan/(.*).html",)), follow=True),
        #Rule(LinkExtractor(allow=("html/gndy/jddy/(.*?).html",)), follow=True),
        Rule(LinkExtractor(allow=r"html/gndy/\w+/\d+/\d+.html"), callback='parse_job', follow=True),
    )

    def parse_job(self, response):

        soup_movie = bs4.BeautifulSoup(response.text, 'html.parser')
        title = response.xpath('//*[@id="header"]/div/div[3]/div[3]/div[1]/div[2]/div[1]/h1/font/text()').extract()[0]
        urldownload = soup_movie.find('div', id="Zoom").find('span').find('table').find('a')['href']
        types = soup_movie.find('div', id="Zoom").find('span').find('p').text.replace(' ', '').replace('\n','').strip()
        regen=r"(.*?类.*?别.*?([\u4E00-\u9FA5].*?)◎)"
        p = r"(.*?\w评分.*?([0-9]*\.?[0-9]+.*?)◎)"
        con = r'(.*?简.*?介.*?([\u4E00-\u9FA5].*?)……)'
        con2 = r'(.*?简.*?介.*?([\u4E00-\u9FA5].*)。)'
        type_movie = re.match(regen, types)
        grade = re.match(p, types)
        content = re.match(con, types)
        if type_movie:
            type_movie = type_movie.group(2)
        else:
            type_movie = '无'
        if content:
            content = content.group(2)
        else:
            content = re.match(con2, types).group(2)
        if grade:
            grade = grade.group(2)
        else:
            grade = '无'
        movie_item = YdDyItem()
        movie_item['title']= title
        movie_item['url'] = response.url
        movie_item['url_object_id'] = get_md5(response.url)
        movie_item['type_movie'] = type_movie
        movie_item['grade'] = grade
        movie_item['content'] = content
        movie_item["urldownload"] = urldownload
        print(movie_item)
        return movie_item
        