# -*- coding: utf-8 -*-
from fake_useragent import UserAgent
import random
import os
import sys
BASE_DIR=os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0,os.path.join(BASE_DIR,'ArticleSpider'))

# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#ua = UserAgent(verify_ssl=False)
#USER_AGENT = ua.random
USER_AGENT='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
#USER_AGENT="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER"
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32
#HTTPERROR_ALLOWED_CODES=[301]#解除重定向
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = int(random.randint(1,2))
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = True
#COOKIES_DEBUG =True
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.ArticlespiderSpiderMiddleware': 543,
#}
##DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
     #'ArticleSpider.middlewares.JSPageMiddleware': 300,
    #'ArticleSpider.middlewares.RandomUserAgentMiddlware': 3,
    #'ArticleSpider.middlewares.RandomProxyMiddleware': 2,
   # 'ArticleSpider.middlewares.ProxyPoolMiddleware': 5,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
    #'ArticleSpider.pipelines.JsonExporterPipeline': 2,
    #'scrapy.pipelines.images.ImagesPipeline':1,
    #'ArticleSpider.pipelines.ArticleImagePipeline': 1,
    #'ArticleSpider.pipelines.MysqlTwistedPipline': 2,
    'ArticleSpider.pipelines.ElasticsearchPipeline':5,
    #'scrapy_redis.pipelines.RedisPipeline': 300
}
IMAGES_URLS_FIELD = 'front_image_url'
project_dir=os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE =os.path.join(project_dir,'images')
#IMAGES_MIN_HEIGHT =100
#IMAGES_MIN_WIDTH =100

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'scrapy'         #数据库名字，请修改
MYSQL_USER = 'root'             #数据库账号，请修改
MYSQL_PASSWD = '634498'         #数据库密码，请修改
MYSQL_PORT = 3306
SQL_DATETIME_FORMAT="%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"


#RANDOM_UA_TYPE="random"
# 调度器启用Redis存储Requests队列
#SCHEDULER = "scrapy_redis.scheduler.Scheduler"


#DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 将Requests队列持久化到Redis，可支持暂停或重启爬虫
#SCHEDULER_PERSIST = True
